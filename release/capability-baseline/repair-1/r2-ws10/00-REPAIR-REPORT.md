# P2-AR-0031 — Repair iteration 1, round 2, WS-10: research, experiment and test-data lifecycles

| Field | Value |
|---|---|
| Run | P2-AR-0031, fresh `capability-repair` builder, model Claude Opus 5 (1M context), `claude-opus-5[1m]` |
| Handoffs | P2-HO-0029 (WS-10), P2-HO-0020 (round-2 common), P2-HO-0010 (common protocol) |
| Branch / base | `phase2/repair-1-r2-ws10` from `843d79c33e8a8db8b223611abc23d317edbc82a1` (integrated round-1 tree, `product_code_digest b1ab1c8c…fbb1`) |
| Work commit (product) | `25edc5a67bd725c5fe0420540879a3ef02d0f673` — `product_code_digest 9456fb927f528f2e8d4d4fe52f32d07d854cb3fd84442e08a40cbf0169d0fe40` (`release/orchestration/phase-2/tools/product_identity.py`); `governed_state_digest` unchanged (`4981437f…227d`) |
| Binaries | after `eb9e9e6e…a211` (release, `25edc5a`); before `7095d188…0332` (release, `843d79c`) — `evidence/BINARY.txt` |
| Classes | BC-P2-47 (J1), BC-P2-48 (J2), BC-P2-46 (H4, with the data-authorship part of BC-P2-34) — each `REPAIRED_CLAIMED` for the WS-10 side (`claims.yaml`) |
| Verdict | `READY_FOR_INDEPENDENT_CAPABILITY_VERIFICATION` — no owner question; the remaining Accept lines sit at call sites other workstreams own and are recorded as integration points (§5) |

This is a builder's claim. Everything below is regression evidence (Contract v3 O3); acceptance is for the fresh independent
verifiers. "Before" = the base binary on a `git archive` of `843d79c`; "after" = the binary of `25edc5a` on this worktree.

---

## 0. What was built

A new module `runtime/src/lifecycle/` (4 files, ≈4 500 lines with tests) owns the three lifecycles as governed records and
state machines. It uses the round-1 APIs rather than re-inventing them:

| Used API (owner) | For |
|---|---|
| `records::Record::edges()`, `graph::identity::identity` (WS-4) | influence/reliance derivation (canonical outgoing edges), `show` identity |
| `t2::seal_record` / `verify_record` / `require_verified` (WS-3) | every lifecycle write is sealed; lifecycle facts (experiment state, runs, reproducibility, promotion, data authorship) are honoured only while the seal verifies |
| `gates::create_system`, `gates::human_approval_for`, `gates::verified_decision` (WS-3) | experiment promotion gate and owner-signed approval bound to a subject digest; real-data approval and independence waivers |
| `orchestration::tasks::is_production_path`, `production_merge_findings` (WS-5) | the production tree; experiment-task output that reached it |
| `control::guard_write`, `authority::require`, `COMMAND_GUARDS` / `g0_label` (WS-3) | every command guarded and classified |

| Surface | Commands (all G0-classified; writes `mutate_spec_other`, promote `approve_cit_human`, reads `read`) |
|---|---|
| J1 | `gov research record [--draft] [--task] \| update \| conclude \| withdraw \| show \| check \| sync` |
| J2 | `gov experiment design \| update \| run \| reproduce \| conclude \| promote \| abandon \| show \| check` |
| H4 | `gov data register \| show`, `gov scenario trace \| check` |

Schemas (kernel payload, version 1.1.0): `research.schema.json` and `experiment.schema.json` now encode J1/J2 completeness
for records presented as evidence; `scenario.schema.json` documents the chain fields (no new requirement — §6.2 explains why).

---

## 1. BC-P2-47 — research output completeness (Contract v3 J1, lines 596-605; framework §45)

**Requirement** (repair-delta BC-P2-47). A research record is not treated as governed evidence (EVIDENCE class, retrievable
as current, citable by a decision) unless it records question/reason, method, sources/data, measurements, uncertainty,
conclusion and confidence; incomplete ones are refused or held reference-only and reported; the output records the
decisions/tasks it influenced.

### 1.1 What changed

| Where | What |
|---|---|
| `research.schema.json` | `$defs/j1_complete`: `question`, `reason`, `method`, `sources` or `data` (non-empty), `measurements` (non-empty), `uncertainty`, `conclusion` (non-blank), `confidence` (number in [0,1]). Required (a) for a current record presented as evidence — `state_class` absent (the `AUTHORITY_POLICY` default for research is EVIDENCE) or EVIDENCE/AUTHORITATIVE/DERIVED — and (b) for `research_state: CONCLUDED`. `research_state` FRAMED/IN_PROGRESS/WITHDRAWN requires `state_class` NARRATIVE/HISTORICAL (framework §45 "reference only until transformed"). |
| `lifecycle::research` | State machine FRAMED → IN_PROGRESS → CONCLUDED, → WITHDRAWN (`RESEARCH_TRANSITION_INVALID`). `record` refuses incomplete research as evidence (`RESEARCH_INCOMPLETE`, naming each missing item) unless `--draft`, which records it FRAMED/IN_PROGRESS and NARRATIVE; `conclude` requires every J1 field and makes it EVIDENCE; `update` edits drafts only (concluded research is superseded, not edited); references (`data`, id-shaped `sources`, `influences`, `--task`) must resolve. Every write stamps `recorded_by`/`concluded_by` and the lifecycle history and is T2-sealed. |
| `lifecycle::research::status` | Standing computed from content, never stored: GOVERNED_EVIDENCE only when current, presented as evidence, complete and CONCLUDED; REFERENCE_ONLY (NARRATIVE/HISTORICAL); INCOMPLETE (a violation); NOT_CURRENT. |
| `lifecycle` (shared) | `cited_evidence` / `influenced_by`: a record relies on research through its canonical outgoing reliance edges (`Record::edges()`: DERIVED_FROM, CONSUMES, GOVERNED_BY, …) or `evidence_refs`; a decision derived from a gate relies on what the gate relies on. `record_influence` writes the backlink (re-sealing only a record whose seal verified — the OS never blesses content it did not write); `sync_influences` (`gov research sync`) reconciles all. `require_citable` refuses `EVIDENCE_NOT_CITABLE`. `indexed_state_class` is the retrieval standing (non-governed evidence held NARRATIVE). |
| findings | `RESEARCH_INCOMPLETE_EVIDENCE` (medium), `RESEARCH_PRESENTED_AS_AUTHORITY` (medium), `RELIES_ON_UNGOVERNED_EVIDENCE` (high for a decision/gate/CIT, medium otherwise — Gate J challenges "unsupported research conclusion", "decision taken before required evidence"), `INFLUENCE_NOT_RECORDED` (medium), `INFLUENCE_UNKNOWN`, `RESEARCH_SOURCE_UNKNOWN` (low). |

### 1.2 Product checks that own it

The schema is enforced by **CIT execution** (`append_record` validation and post-execution `schema_validation`) and by the
suite family **`schema_invariants`** (scheduler tiers G1 G2 G4 G5 G6). The lifecycle findings run in `gov research check`
and are written for the suite family WS-2 registers (IP-WS10-06). Unit tests: `lifecycle::research::tests::{j1_completeness_decides_evidence_standing, findings_name_incomplete_evidence_unsupported_decisions_and_missing_backlinks}`, `lifecycle::tests::influence_is_derived_through_edges_evidence_refs_and_gates`.

### 1.3 Probes re-run

| Line (delta-r `J1-J2-research-experiments`, shim mode) | Before | After |
|---|---|---|
| J1.a.question … J1.a.confidence, J1.a.graph | PASS | PASS |
| **J1.b.accepted** (CIT appends research with only question + conclusion) | FAIL (`COMMITTED`) | **PASS** (`SCHEMA_INVALID`: reason, method, sources, measurements, uncertainty, confidence) |
| **J1.b.audit** (suite flags RES-0100/0101/0102) | FAIL (HEALTHY, no finding) | **PASS** (`schema_invariants`: RES-0101, RES-0102 named) |
| J1.a.influences (benchmark record's `influences` non-empty right after `--record`) | FAIL | FAIL — `memory::benchmark` is WS-6's (IP-WS10-04; see §1.4) |
| J1.a.influence_backlink (after `memory select --research`) | FAIL | FAIL — `memory select` does not call the backlink yet (IP-WS10-03). With `gov research sync` it is recorded (supplementary WS10-J1-8). |
| OBSERVE J1.b.retrieval / J1.b.decision | EVIDENCE retrieved / decision taken | unchanged surfaces (WS-6 indexer IP-WS10-05; WS-3 gates IP-WS10-02). The decision is now reported: `RELIES_ON_UNGOVERNED_EVIDENCE` (high) — WS10-J1-6 |

Supplementary (`evidence/probes/ws10_supplementary.py`, real `gov` processes on disposable projects): WS10-J1-1…9 **9/9** after,
**0/9** on the base binary — incomplete research refused with the missing items named; complete research CONCLUDED/EVIDENCE/T2
VERIFIED; drafts NARRATIVE and cannot claim EVIDENCE; FRAMED→IN_PROGRESS→CONCLUDED; no re-conclusion; a CIT refuses incomplete
evidence and accepts a NARRATIVE note (control); the suite (`schema_invariants`) flags hand-written incomplete evidence and not the
note; a gate and a decision taken on incomplete research are reported high while one on governed research is not; the backlink
is reported until recorded and recorded by `sync` with the seal kept; the product's own benchmark→select decision is recorded
once reconciled; SKL-RESEARCH-BENCHMARK V1's executable check is now true (IP-WS02-21, §4).

### 1.4 Limits

* **J1.a.influences as the probe states it** requires the benchmark research to list influenced decisions/tasks *at creation*,
  before anything was influenced. The requirement as I read it (repair-delta: "the output records the decisions/tasks it
  influenced") is met by maintaining the backlink when a decision/task derives from the research. IP-WS10-04 asks WS-6 to record
  the commissioning task (`--task`) at creation and IP-WS10-03 to call `record_influence` in `memory select`; after both, both
  lines hold.
* Retrieval of incomplete research as EVIDENCE and refusal of a gate/decision citing it happen in WS-6/WS-3 files (IP-WS10-05,
  IP-WS10-02). Until then, the suite (schema) and `gov research check` report them.
* The write commands need `mutate_spec_other` (L2); the L1 `research-agent` cannot use them (IP-WS10-01). It can still author a
  research file in a task and close it; `gov research check`/the schema judge it the same way.

---

## 2. BC-P2-48 — experiment lifecycle (Contract v3 J2, lines 607-614; challenge "irreproducible experiment", line 616)

**Requirement** (repair-delta BC-P2-48). Experiments are governed through a lifecycle recording hypothesis/question,
method/data, reproducibility, results, interpretation and decision influence; experimental output cannot enter the production
tree without a governed promotion. Dep: BC-P2-14 (WS-5's close refusal, in the base).

### 2.1 What changed

| Transition | Operation | Requires (typed refusal) |
|---|---|---|
| — → DESIGNED | `gov experiment design` | hypothesis or question, method, data (`data` ids / `data_provenance` / `inputs`) (`EXPERIMENT_DESIGN_INCOMPLETE`); outputs outside the production tree (`EXPERIMENT_OUTPUT_IN_PRODUCTION`); never `production_merge_allowed: true` (`PRODUCTION_MERGE_NOT_ALLOWED`); no OS-owned fields (`OS_OWNED_FIELD`). An existing experiment record outside the lifecycle is adopted under its own id (merge flag corrected). |
| DESIGNED → RUNNING | `gov experiment run --results` | the primary run: results + SHA-256 digest, every input bound by content (record digest without OS bookkeeping; files/dirs at `location`/`inputs`), environment, role, session, task; a missing input refuses (`EXPERIMENT_INPUT_MISSING`); one primary run (`EXPERIMENT_ALREADY_RUN`) |
| RUNNING/CONCLUDED/PROMOTED | `gov experiment reproduce --results` | OS judges agreement with the primary run under the acceptance rule fixed at design (`exact`, or numeric `tolerance`), whether it ran on the same input bytes and whether it is independent (another session); `reproducibility.status` = NOT_REPRODUCED once any same-input reproduction disagrees (sticky), REPRODUCED if one agrees, else UNVERIFIED |
| RUNNING → CONCLUDED | `gov experiment conclude` | interpretation, decision_influence, confidence, reproducibility procedure + environment (`EXPERIMENT_CONCLUSION_INCOMPLETE`); results are the primary run's, copied by the OS (asserting results or changing the design/acceptance rule: `EXPERIMENT_DESIGN_FROZEN`) |
| CONCLUDED → PROMOTED | `gov experiment promote --paths [--gate] [--cit]` | L3 (`approve_cit_human`); governed evidence and an independent agreeing reproduction (`EXPERIMENT_NOT_PROMOTABLE`); production paths only. Without `--gate` the OS raises a Human Decision Gate (`gates::create_system`, trigger `experiment_promotion`, full package) whose `subject.sha256` binds experiment, primary results digest, agreeing reproductions and the exact paths; with `--gate` it applies only an owner-signed, authorising human answer for exactly that subject (`gates::human_approval_for`: `HUMAN_APPROVAL_REQUIRED`, `GATE_DECLINED`, `APPROVAL_STALE`). |
| DESIGNED/RUNNING/CONCLUDED → ABANDONED | `gov experiment abandon --reason` | fail-safe direction: allowed on an unverified record |

Every transition is T2-sealed; gov refuses to build on lifecycle facts whose seal does not verify (`T2_UNBOUND`).
`lifecycle::experiment::status`: GOVERNED_EVIDENCE only when current, CONCLUDED/PROMOTED, OS-written, complete, REPRODUCED, and
every input still hashes as at the primary run; otherwise UNGOVERNED / REFERENCE_ONLY / INCOMPLETE / IRREPRODUCIBLE (with the
disagreeing runs or the changed inputs named). The OS sets `state_class` EVIDENCE only for a reproduced concluded experiment.

**Production merge** (`lifecycle::experiment::findings`, `gov experiment check`): declared outputs inside the production tree;
**any production file byte-identical to an experimental output file** (whatever its name) not covered by the approved
promotion; experiment-class task output that reached production (WS-5's `tasks::production_merge_findings`, re-shaped); a
PROMOTED experiment whose promotion is no longer honoured (gate revoked or re-answered). A promotion covers paths only while
its gate's owner-signed answer still verifies for the recorded subject. Exposed for round 3: `promotion_refusal` (a CIT that
carries experimental output into production must be covered — IP-WS10-09) and `task_lifecycle_refusal` (an experiment task
closes only when linked to an experiment with a recorded run — IP-WS10-11).

`experiment.schema.json`: current experiments presented as evidence carry `experiment_state` + the design; CONCLUDED/PROMOTED
carry results, reproducibility (procedure, environment), interpretation, decision_influence, confidence; PROMOTED carries
promotion (gate, paths, subject_sha256); DESIGNED/RUNNING are NARRATIVE; ABANDONED has a reason; `production_merge_allowed`
stays `const false`.

### 2.2 Product checks that own it

CIT execution and `schema_invariants` (schema); every `gov experiment` transition (state machine, T2); `gov experiment check`
and the family of IP-WS10-06 (standing, reproducibility, drift, production merge, reliance, influence). Unit tests
`lifecycle::experiment::tests::{the_state_machine_admits_only_its_transitions, reproductions_are_judged_by_the_os_under_the_fixed_rule,
standing_requires_os_written_concluded_reproduced_experiments_on_unchanged_inputs, experimental_output_copied_into_production_is_found_unless_promoted}`.

### 2.3 Probes re-run

| Line (delta-r `J1-J2`) | Before | After |
|---|---|---|
| **J2.empty** (CIT appends an experiment with nothing but a title) | FAIL (`COMMITTED`) | **PASS** (`SCHEMA_INVALID`: experiment_state, method, hypothesis/question, data) |
| OBSERVE J2.schema | decision_influence/interpretation/reproducibility absent | every J2 item has a field |
| OBSERVE J2.cli | `unrecognized subcommand 'experiment'` | exit 0 |
| J2.merge.schema, J2.merge.flag, J2.merge.flag2, J2.merge.enforced | PASS | PASS |
| J2.incomplete.audit | FAIL | FAIL — **vacuous** (§2.4) |
| J2.merge.detected (suite finding) | FAIL | FAIL — the suite family is WS-2's (IP-WS10-06); the same scenario is detected by `gov experiment check` (WS10-J2-9) |

Supplementary WS10-J2-1…11: **11/11** after, **0/11** before — design refusals; transition refusals, input binding, frozen
results; an unreproduced conclusion is not evidence; an independent reproduction within tolerance makes it governed evidence;
**irreproducible experiment detected** (disagreeing reproduction → NOT_REPRODUCED, sticky, reported; a gate relying on it
reported high); input drift → IRREPRODUCIBLE, restored bytes → governed again; a hand-forged reproduction → T2 BROKEN,
UNGOVERNED, high finding, `reproduce` refused `T2_UNBOUND`; promotion refused while irreproducible, refused with only a
same-session reproduction, refused for an L2 role, refused on an unanswered gate, `APPROVAL_STALE` for other paths, PROMOTED
after the owner-signed answer; experimental bytes copied into production under another name reported, the approved path not;
the delta-r J2.merge scenario detected naming task and file; a legacy experiment reported then adopted; a revoked promotion
gate withdraws the promotion.

### 2.4 Limits

* **J2.incomplete.audit is vacuous after the repair.** The probe checks that the suite flags EXP-0001 — the empty experiment
  that J2.empty tries to append. J2.empty now refuses that CIT, so EXP-0001 never exists. A directly written incomplete
  experiment *is* flagged: J2.merge.schema's detail now lists `EXP-0002: "experiment_state" is a required property`, and
  WS10-J2-10.
* **Reproduction is judged on results supplied by the reproducing session.** The OS cannot re-execute arbitrary experiments;
  it binds inputs by hash, judges agreement under a rule fixed before any run, records who reproduced, and requires a
  *different session* for promotion. Session and role identity are caller-declared (OD-P2-01: agent roles stay
  adapter-declared). Citability requires REPRODUCED (any session); promotion requires an independent one.
* **Copy detection is byte-level.** Experimental output altered on its way into production is caught only through the
  experiment task's observed paths (WS-5) or a CIT declaring the experiment; not by content similarity.
* **T2 is machine-bound** (WS-3 design): an experiment sealed on another machine is FOREIGN, hence UNGOVERNED there.

---

## 3. BC-P2-46 — scenario → data → test-data lineage and provenance (Contract v3 H4, lines 524-527; framework §39), with the WS-10 (data authorship) part of BC-P2-34

**Requirement** (repair-delta BC-P2-46; handoff P2-HO-0029). The FEATURE → SCENARIOS → DATA → TEST DATA → SUCCESS/FAILURE →
INDEPENDENT TESTS chain is machine-traceable through the product's own fields with missing links detected; test data used by
acceptance/independent tests carries recorded provenance and its absence is detected; test-data author independence is
recorded and checked (BC-P2-34's data part; Contract v3:526; framework §39 "normally independent of both the implementation
author and end-to-end test author").

### 3.1 What changed (`lifecycle::scenario`)

| Link | The product's own fields (module doc and `scenario.schema.json` 1.1.0 descriptions) |
|---|---|
| FEATURE → SCENARIO | `feature.scenarios` or `scenario.feature` |
| SCENARIO → DATA | `scenario.data_requirements` (ids of `data` records, `data_kind: requirement`), or a reasoned `data_requirements_not_applicable` |
| DATA → TEST DATA | a `data` record (`data_kind: test-dataset`) naming what it realises in `implements` (also `derived_from`, `realises`, `relations[]`), or the requirement's `test_data` |
| SUCCESS/FAILURE | `scenario.success_criteria`, `scenario.failure_criteria` |
| INDEPENDENT TESTS | `test-obligation.scenario` in a `TEST_POLICY.independent_test_author_required_for` family with `independent_of_implementer: true`, naming its data in `test_data` (also `required_data`, ids named in `data_provenance`) |

* **Missing links** are typed gaps from the records themselves (no index needed): `SCENARIO_WITHOUT_FEATURE`,
  `SCENARIO_WITHOUT_SUCCESS_CRITERIA`, `SCENARIO_WITHOUT_FAILURE_CRITERIA`, `SCENARIO_DATA_UNDECLARED` (a silent N/A is a gap),
  `DATA_REQUIREMENT_NOT_GOVERNED|UNRESOLVED|WRONG_TYPE`, `DATA_REQUIREMENT_WITHOUT_TEST_DATA`, `SCENARIO_WITHOUT_TEST`,
  `SCENARIO_WITHOUT_INDEPENDENT_TEST`, `TEST_DATA_UNDECLARED`, `TEST_DATA_NOT_GOVERNED`, `TEST_DATA_NOT_FOR_SCENARIO`,
  `FEATURE_WITHOUT_SCENARIOS`.
* **Provenance required and read**: `provenance: {source_kind ∈ framework §39's kinds (approved-real, public,
  repository-corpus, synthetic, simulator, fixture), origin}`; `approved-real` must name a decision `gates::verified_decision`
  honours with `human_approved: true`; a `location` is bound by SHA-256 at registration and re-hashed (`TEST_DATA_CHANGED`,
  `TEST_DATA_LOCATION_MISSING`, `TEST_DATA_UNBOUND`); absent/unstructured/invalid provenance are gaps.
* **Authorship recorded by the OS**: `gov data register` stamps role and session (T2-sealed `authorship`); a dataset produced
  inside a task is attributed to the closing session through the report's OS-observed paths; declared `author_role` is a
  claim. **Independence checked** against every implementer of the scenario/feature (designated `role` of each
  implementation-class task and the role/session that closed it) and every end-to-end (independent-family) test author:
  `DATA_AUTHORSHIP_NOT_ESTABLISHED`, `DATA_AUTHOR_NOT_INDEPENDENT` (same role or same session), `DATA_AUTHOR_IS_TEST_AUTHOR`;
  an owner-approved `independence_waiver` decision is the only exception. Registration refuses a non-independent author
  (`DATA_AUTHOR_NOT_INDEPENDENT`) and missing provenance/links (`DATA_PROVENANCE_REQUIRED`, `DATA_CHAIN_INCOMPLETE`,
  `DATA_REFERENCE_UNKNOWN`, `DATA_NOT_A_REQUIREMENT`, `DATA_REAL_DATA_UNAPPROVED`).
* **Exposed for WS-5**: `implementation_blockers(task)` (READY gating on the chain) and `readiness_cells(feature)` (computed
  `success_criteria`, `failure_criteria`, `representative_test_data`, `independent_acceptance_tests` instead of
  author-asserted cells).

### 3.2 Product checks that own it

`gov scenario trace|check`, `gov data register|show`; the suite family of IP-WS10-06. Unit tests
`lifecycle::scenario::tests::{a_complete_chain_has_no_gaps_and_computes_present_cells, every_missing_link_is_a_typed_gap,
provenance_is_read_real_data_needs_approval_and_changes_are_detected,
data_author_independence_uses_recorded_authorship_and_honours_only_an_approved_waiver}`,
`lifecycle::tests::authorship_prefers_the_os_stamp_then_the_closing_report_then_declarations`.

### 3.3 Probes re-run

gamma-r `H4-scenarios-data-tests` prints observations, not verdicts. Its surfaces are `memory graph` (WS-4's relation fields),
`task dag` and `readiness check` (WS-5), and `audit` (WS-2). Those lines are **unchanged** (`evidence/after/`); what changed
is that the source now has consumers of `author_role` and `data_provenance` (the probe's grep lines). The same fixture, traced
by the product (`gov scenario trace F-0001`, WS10-H4-1), names every missing link: `DATA_REQUIREMENT_WITHOUT_TEST_DATA`
(DATA-0001), `TEST_DATA_NOT_FOR_SCENARIO` (TST-0001), `TEST_DATA_UNDECLARED` (TST-0002), `TEST_DATA_WITHOUT_PROVENANCE`,
`DATA_AUTHORSHIP_NOT_ESTABLISHED`, `DATA_AUTHOR_NOT_INDEPENDENT` (TD-0001, authored by the implementer's role).

Supplementary WS10-H4-1…6: **6/6** after, **0/6** before — the gamma-r fixture's gaps; missing criteria; register refusals;
the implementer's role refused as data author while an independent role registers with OS authorship (T2) and a content
hash; the complete chain; a changed dataset reported; real data with an owner-approved decision and an owner-approved waiver
accepted. WS10-G0-1: writes need the declared role's authority and are refused under FREEZE_WRITES; reads answer.

### 3.4 Limits

* H4.b1 as written asks `memory graph` for SCN→DATA, DATA→TD and TD→TST edges. `data_requirements` and `test_data` are not
  relation fields: `records.rs` relation fields are WS-4's (IP-WS10-08). DATA→TD traces through `implements` (already an
  edge). The gamma-r fixture itself has **no** DATA→TD link (TD-0001 names nothing and nothing names it), and names its test
  data only in free text — which the product now reports rather than traces.
* The gamma-r lines "chain refused anywhere" (DAG) and the readiness cells are WS-5's files (IP-WS10-12); the suite lines are
  the family (IP-WS10-06).
* The scenario schema gains no requirement (§6.2): chain gaps are MEDIUM findings, not schema violations.
* Report attribution trusts the OS-minted but not yet T2-sealed report records (WS-5 IP-5); it is labelled as such.
* `data-author` is L1 and cannot run `gov data register` until IP-WS10-01; it establishes authorship today through a task it
  closes.

---

## 4. Integration point routed to WS-10

| IP | From | Status |
|---|---|---|
| IP-WS02-21 | WS-2 (P2-AR-0015): "When BC-P2-47 lands, set SKL-RESEARCH-BENCHMARK V1 to `mode: executable`" | **Precondition met.** The check (write a research record without method; `audit --family schema_invariants` must name it) now holds: `gov health skills --include-deferred --skill SKL-RESEARCH-BENCHMARK` reports `deferred_check.expectation_met: true` (WS10-J1-9). Flipping the mode in `framework/health/SKILL_SCENARIO_CHECKS.yaml` is WS-2's (IP-WS10-07). |

---

## 5. New integration points (round 3)

| IP | Owner · file / function | Exact change | Closes |
|---|---|---|---|
| IP-WS10-01 | WS-3 · `framework/policies/AUTHORITY_POLICY.yaml` (+ `ENFORCEMENT_MAP`) | Declare an L1 class for recording research and test data (e.g. `record_research_evidence: L1`), then set `lifecycle::RECORD_AUTHORITY` to it and the twelve matching `COMMAND_GUARDS` entries (a unit test keeps them equal) | L1 `research-agent`/`data-author` (framework §23 "scoped document mutation") can record through gov |
| IP-WS10-02 | WS-3 · `gates::create` (fields `derived_from`) and `gates::answer` (`req.evidence`, and the gate's `derived_from`) | Before persisting: `crate::lifecycle::require_citable(p, &store, &cited)?`; after persisting the gate / the decision: `crate::lifecycle::record_influence(p, &cited, &id)?` | J1 "citable by a decision" (OBSERVE J1.b.decision); J1/J2 influence backlinks |
| IP-WS10-03 | WS-6 · `memory::benchmark::select` | `crate::lifecycle::require_citable(p, &store, &[research])?` before the decision; `crate::lifecycle::record_influence(p, &[research], &did)?` after | J1.a.influence_backlink |
| IP-WS10-04 | WS-6 · `memory::benchmark::run` (`--record`) | Accept `--task <TASK>` (the commissioning task) and write it in `influences`; write `research_state: CONCLUDED` and seal with `t2::seal_record` like `gov research record` | J1.a.influences |
| IP-WS10-05 | WS-6 · `memory/indexer.rs` (state class of an indexed record) | For research/experiment records use `crate::lifecycle::indexed_state_class(&Ctx::new(p, &store), &r)` instead of `state_class_for` | OBSERVE J1.b.retrieval ("not retrievable as current") |
| IP-WS10-06 | WS-2 · `verification::run_family`, `TEST_POLICY.governance_families`, `scheduler::catalogue` | New family `research_experiment_data_lifecycle`: push each of `crate::lifecycle::suite_findings(p, store)` and `crate::lifecycle::experiment::task_merge_findings(p, store)` as `finding(f.severity, fam, f.message, f.path)`; tiers G2/G5 (chain of the closing task at G2); block rules at WS-2's judgement | J2.merge.detected; H4.b1/b2/b3 suite lines; the J1/J2 reliance/influence/irreproducibility findings at a G-tier |
| IP-WS10-07 | WS-2 · `framework/health/SKILL_SCENARIO_CHECKS.yaml` | SKL-RESEARCH-BENCHMARK V1 `mode: deferred` → `executable` (IP-WS02-21) | skill regression truth |
| IP-WS10-08 | WS-4 · `records.rs` `RELATION_FIELDS` | Add `("data_requirements", "CONSUMES")`, `("test_data", "CONSUMES")`, `("realises", "IMPLEMENTS")`; the edge derivation changes, so force a full rebuild (`INDEX_VERSION`, WS-4 IP-17) | H4.b1 graph edges SCN→DATA, TST→TD |
| IP-WS10-09 | WS-4 · `cit::approve`, `cit::execute` | `if let Some(e) = crate::lifecycle::experiment::promotion_refusal(&crate::lifecycle::Ctx::new(p, &store), &cit) { return Err(e) }` | J2 "cannot enter production without a governed promotion" at the CIT that would carry it |
| IP-WS10-10 | WS-4 · `context::manifest` (evidence inputs) | For a research/experiment input whose `crate::lifecycle::evidence_status` is not citable, add an advisory problem `EVIDENCE_NOT_GOVERNED` (flag, like `authority_flag`) | a task packet never presents unsupported research as evidence |
| IP-WS10-11 | WS-5 · `tasks::close` (class `experiment`) | `if let Some(e) = crate::lifecycle::experiment::task_lifecycle_refusal(&ctx, &t) { refuse unless --force, recording the override }` | experiments governed through the lifecycle |
| IP-WS10-12 | WS-5 · `dag::compute`, `readiness::evaluate` | Blocked reasons from `crate::lifecycle::scenario::implementation_blockers(&ctx, t)` for implementation-class tasks; readiness cells `success_criteria`, `failure_criteria`, `representative_test_data`, `independent_acceptance_tests` from `crate::lifecycle::scenario::readiness_cells(&ctx, feature)` | H4 "missing links detected" at READY; gamma-r H4.b1 DAG line, readiness "author-asserted" line; H3 |
| IP-WS10-13 | WS-5 · `framework/schemas/test-obligation.schema.json`; `tasks::create` | Declare `test_data` (array of data record ids); after `tasks::create` with evidence ids in `derived_from`/`required_inputs`: `crate::lifecycle::record_influence(p, &cited, &id)` | the product's documented TEST DATA → TESTS field; task influence backlink |
| IP-WS10-14 | WS-1 · `tests/governance/capability-evidence-map.yaml` | H4 → `lifecycle::scenario::tests::*`, `gov scenario check`, family IP-WS10-06; J1 → `lifecycle::research::tests::*`, `schema_invariants` (research), `gov research check`; J2 → `lifecycle::experiment::tests::*`, `schema_invariants` (experiment), `gov experiment check`, family IP-WS10-06 | AC-10 evidence owners |
| IP-WS10-15 | WS-3 · `gates::HUMAN_ONLY_TRIGGERS` (optional) | Add `experiment_promotion` so an agent resolution is refused at answer time too (promotion already accepts only `by_kind: human` through `human_approval_for`) | defence in depth |
| IP-WS10-16 | release/migration authors (WS-8 / WS-9) · next framework migration | Note (migrations may not touch `spec/`, INV-013): research/experiment schemas 1.1.0 — incomplete research/experiment records presented as evidence are now schema HIGH; remediation: `state_class: NARRATIVE`, or `gov research conclude` / `gov experiment design` | upgrade path (`update --apply` refuses only on critical, so it is not blocked) |
| IP-WS10-17 | docs owner · `docs/COMMANDS.md` | Document `gov research|experiment|data|scenario` and their refusal codes | — |

Changes of mine in files owned by others (all additive, per the handoff): `cli/src/main.rs` (four `Cmd` variants, their
subcommand enums, `g0_label`/`command_name`/`run` arms, one `lifecycle_cmd` dispatcher, in a marked WS-10 block),
`runtime/src/orchestration/control.rs` (twenty `COMMAND_GUARDS` entries with their rationale), `runtime/src/lib.rs`
(`pub mod lifecycle;`). No `tasks.rs`, `verification/**`, `records.rs`, `gates.rs`, `memory/**`, `srr/**` or policy file was
touched.

---

## 6. Effect on the other audits of record

The schema change makes the suite flag research/experiment fixtures that present incomplete evidence. I re-ran every
audit-of-record probe whose fixture writes research, experiment or scenario records, plus the command-surface/health probes,
**unedited**, before and after (`evidence/run-audit-probe.sh`; shim mode = the integration's unedited owner-channel adapter).
`evidence/probe-reruns/COMPARE.out` (verdict markers) and `normdiff/` (normalised diffs of every output, all reviewed):

| Probe | Verdict change | Cause |
|---|---|---|
| delta-r J1-J2 | FAIL→PASS J1.b.accepted, J1.b.audit, J2.empty | the repair |
| zeta-r W07 | FAIL→PASS W7-o3, W7-o3b | **spurious — not an orphan-detection repair.** The probe credits any surface naming RES-0001/RES-0002; they are now named by `schema_invariants` because the fixture's research lacks J1 fields. BC-P2-22 (orphans) is untouched. |
| beta-r C8 | PASS→FAIL C8-b5 | **fixture effect**: the check needs the baseline audit HEALTHY/DEGRADED, and the beta-r synthetic project (`lib/synth.py`) holds RES-0101 (question, conclusion, confidence) and EXP-0001 (hypothesis, method, result) presented as evidence — now 5 HIGH schema findings. |
| beta-r D2 | probe stops at its required `gov audit` (exit 1) | the same fixture effect |
| beta-r C1, C2, D5, FRESH; epsilon-r U; zeta-r W01 | none | additive schema findings on the same kind of fixture records; beta-r FRESH `result-changed-on-rerun` rows read False because the verdict stays UNHEALTHY; epsilon-r U's doctor gains D031 (below) |
| delta-r FRESH, K1, K2, K3; gamma-r H1, H2H3, I1I2, H4; alpha-r A4; zeta-r W02, W04b; epsilon-r O2, O4; beta-r C9, X-K2-D1-W6 | none | identical after normalisation except retrieval-rank/latency/race noise (K1 tail candidate, O2 claim-sweep race, C9 dict order, W04b latency) and additive grep lines (I1I2, H4) |

**Derived-fixture demonstration** (`evidence/derived/`): a labelled copy of beta-r `lib/synth.py` whose only change holds
RES-0101 and EXP-0001 reference-only (`state_class: NARRATIVE`; `.diff` beside it). With it, C8 and D2 produce verdict lines
**identical** before and after, and identical to the unedited base run — the probes' own properties are unaffected.

### 6.1 A consequence to state plainly

A schema violation is HIGH in `schema_invariants` (WS-2), and WS-2's scheduler turns a HIGH `schema_invariants` finding into
a hard-block on state-relying operations (`task.close` via `close_gate`, `cit.execute`, `release.build`, `update.apply`; doctor
D031 shows it — epsilon-r U). So one hand-written research note that presents itself as evidence without method,
measurements etc. makes the suite UNHEALTHY and, once WS-5 wires `close_gate`, refuses those operations until it is completed
or held reference-only (`state_class: NARRATIVE`, or `gov research update <id> --fields '{}'`). This follows from the kernel's
own authored expectation — SKL-RESEARCH-BENCHMARK V1: "research record without method → schema validation fails" — and
WS-2's rule for invalid governed records; it is the same consequence the base product already gives an experiment declaring
`production_merge_allowed: true`. `update --apply` refuses only on critical findings, so upgrades are not blocked (IP-WS10-16).
I record it as a design consequence, not an owner question: the sources fix both the schema expectation and the blocking rule.
If a verifier or the owner prefers J1/J2 incompleteness to be reported without blocking, the alternative is to drop the
`allOf` completeness rules from the two schemas and rely on the lifecycle family (medium) — at the cost of J1.b.accepted,
J1.b.audit, J2.empty and SKL-RESEARCH-BENCHMARK V1.

### 6.2 Why the scenario schema gains no requirement

CIT propagation marks affected scenarios stale and then schema-validates every touched record (`CHANGE_POLICY.verification_required:
schema_validation`). Requiring success/failure criteria or data declarations in the scenario schema would make an unrelated CIT
fail and roll back whenever it reaches an incomplete scenario (delta-r K2's fixture scenario has neither). Chain gaps are
therefore MEDIUM lifecycle findings, and the scenario schema only documents the chain fields.

---

## 7. Regression and preservation

| Suite | Base `843d79c` (integration report) | Final `25edc5a` | Evidence |
|---|---|---|---|
| `cargo test --lib` | 146 / 0 | **160 passed, 0 failed** (+14 `lifecycle::*`) | `evidence/regression/cargo-test-lib.out` |
| `cargo test --test certification` | 100 / 0 | **100 passed, 0 failed** (incl. `section6::*`, `ws03::every_cli_command_label_is_classified_by_g0`) | `evidence/regression/cargo-test-certification.out` |
| `rustfmt --check` (edition 2021) on every touched Rust file | — | 0 hunks each (`lib.rs`: the 14 pre-existing recursive hunks, same as base) | `evidence/regression/rustfmt-check.out` |
| `cargo clippy` (lifecycle files) | — | no warning | — |
| builder probe `ws10_supplementary.py` | 1 / 35 (the control only) on the base binary | **35 / 35** | `evidence/probes/` |

No builder test was changed. `CARGO_BUILD_JOBS=2` throughout.

**R1 held-out suites.** No SRR, kernel, lock, init, update, release, recovery, records, tools/capabilities or §6-sink file
changed; I ran them anyway because the module adds functions (AR-0033's census) and calls §6 sinks (`save_record`,
`gates::create_system`). Per P2-HO-0020 item 7, `evidence/r1-heldout/run-r1-heldout.sh` builds each suite against **this
worktree through a new private scratch root per run** (`mktemp -d`; the `wt/srr1-r1-verify*` symlinks can point nowhere
else). Results: §7.1.

### 7.1 R1 held-out results

Run `final` (`evidence/r1-heldout/r1-heldout-final.out`) at `25edc5a`, private scratch root
`…/p2ar0031/r1-p2ar0031-final-qopb58` whose `wt/srr1-r1-verify*` point at this worktree (recorded in the header); all 27
copied suite files `cmp`-identical to the held-out evidence.

| Suite | Recorded baseline (integration `811317b`) | This tree `25edc5a` |
|---|---|---|
| AR-0027 (`4.1.6-r1`) | 26 / 3 (`b1`, `b2`, `d3`) | **26 / 3**, same tests |
| AR-0029 (`4.1.6-r1-2`) | 26 / 2 (`b3`, `b6`); `ho_f_preservation` does not compile | **26 / 2**, same tests; `ho_f` does not compile (same) |
| AR-0031 (`4.1.6-r1-3`) | 27 / 7 (`a1`, `a5`, `a8`, `b6`, `c2`, `c3`, `d2`) | **27 / 7**, same tests |
| AR-0033 (`4.1.6-r1-4`) | 30 / 1 (`hv_a::a1`, its 84-file / 740-function pin) | **30 / 1**, same test |

**The census that identifies the tree** (P2-HO-0020 item 7): AR-0033's derived copy with only the two scale assertions
replaced by prints (S1, `r1-heldout/hv_a_derivation.a1-unpinned.P2-AR-0031.rs.txt`, byte-identical to P2-AR-0022's; the
`diff` in the output shows exactly those two lines) walks **109 files / 1581 functions** — the integration's 105 files plus
this run's four `lifecycle/` files — with **0 violations in every §6 activity**: human_gate_create 45 derived / 40 writers /
1 exempt (integration: 43 / 38 / 1 — the lifecycle functions that persist through `save_record` are derived and accepted by
that sink); human_gate_approve 1/1; release_certification 1/1; trust_policy_mutation 8/1; privileged_plugin_acquisition 10/2;
floor_lower_or_reset 3/1; present_below_floor_release_as_current 1/1. AR-0033's own `derive.py` (S2, `ROOT` line only
substituted) agrees under all three splitter configurations, 0 violations.

---

## 8. Owner-decision questions

None. No class required changing an accepted architecture or trust boundary, a new external dependency class, or
owner-controlled material. Two design points a verifier may weigh, stated in §6.1 (schema HIGH and WS-2's hard-block) and
IP-WS10-01 (L2 vs L1 authority for recording research and test data — WS-3's policy file).

---

## 9. Evidence index (`evidence/`)

| Path | Content |
|---|---|
| `BINARY.txt` | work commit, after/before binary SHA-256 |
| `run-audit-probe.sh` | private-path runner for audit-of-record probes (derived from the integration's; parameters: binary, tree, output) |
| `before/`, `after/` | delta-r `J1-J2-research-experiments` (shim) and gamma-r `H4-scenarios-data-tests` (integrated), unedited |
| `probe-reruns/{before,after}/`, `COMPARE.out`, `normdiff/` | the cross-family set of §6 and its comparison; `compare_probe_reruns.py` produced them |
| `derived/` | the labelled beta-r `synth.py` copy + `.diff`; C8/D2 outputs with it, before and after |
| `probes/ws10_supplementary.py`, `ws10-supplementary.after.out`, `ws10-supplementary.base-negative-control.out` | builder probe (35 checks) and its negative control |
| `regression/` | `cargo test --lib`, `--test certification` (final, and the earlier `.dev` runs), rustfmt |
| `r1-heldout/` | runner, the (S1) derived copy of `hv_a::a1` (scale pins printed, not asserted), `r1-heldout-final.out` |

Outputs carry absolute scratch paths of this run. Scripts take `P2AR0031_SCRATCH` (and `GOV_UNDER_TEST`/`TREE`/`OUTD`, or
`GOV_BIN`/`PROBE_SCRATCH`) and write only there or under this directory.

## 10. Process disclosures

* Model Claude Opus 5 (1M context), `claude-opus-5[1m]`. No sub-agents; the owner was not contacted; no session or agent
  transcripts, task-output stores or user auto-memory were read. Two long cargo runs continued in the background after the
  tool timeout; their output was redirected into `evidence/regression/` and `evidence/r1-heldout/`, which is where I read it.
* An early `cargo fmt -- <files>` formatted the whole workspace (it passes files *in addition to* the crate). I reverted the
  four unowned files it touched (`srr/breakglass.rs`, `srr/metadata.rs`, `tests/certification/{section6,srr}.rs`) before any
  commit; afterwards only `rustfmt` on my own files was used. `cli/src/main.rs` and `control.rs` were already rustfmt-clean
  at base, and their diffs are insertions only.
* Commands containing `rm -rf`/`rm -f` were denied by the permission system and not retried as written; scratch work uses fresh
  `mktemp -d` directories instead.
* The builder probe's human answers provision a **standalone** human-channel anchor on an unprovisioned machine, which is this
  tree's default (`standalone_anchor_when_unprovisioned: true`). P2-ADJ-0001 routes the default to `false` in WS-3's round-2
  work (OWNER-DECISION-P2-0002: provision, then work). The product code does not depend on it — promotion, real-data approval
  and waivers go through `gates::human_approval_for` / `verified_decision`, whatever anchor verifies — but after that change
  the probe's gate answers need a machine provisioned with a throw-away root that delegates `human-gate` (as WS-8's
  certification tests do). OWNER-DECISION-P2-0001 (agent roles stay adapter-declared) is why test-data authorship and
  reproduction independence rest on declared role and session.
* No file under `release/verification/`, `release/root-of-trust/`, `release/releases/`, `release/orchestration/phase-1/`,
  `release/capability-baseline/audit-0/` or another workstream's `repair-1/` directory changed; Contract v3 is byte-identical
  (`4c2df291…5ed3`).
