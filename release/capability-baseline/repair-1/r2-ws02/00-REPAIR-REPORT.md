# P2-AR-0023 — Repair iteration 1, round 2: WS-2 repair report

| Field | Value |
|---|---|
| Run | P2-AR-0023, role `capability-repair`, model Claude Opus 5 (1M context), `claude-opus-5[1m]`, fresh context |
| Handoffs | P2-HO-0021 (WS-2 round 2), P2-HO-0020 (round-2 common), P2-HO-0010 (common protocol) |
| Branch / base | `phase2/repair-1-r2-ws02` from `843d79c33e8a8db8b223611abc23d317edbc82a1` (integrated round-1 tree; `product_code_digest b1ab1c8c…fbb1`) |
| Work commits | `1e75f4b` (main), `4bfc9e5` (hidden-oracle records; untraced-work severity), `4e0f59b` + `5276dfa` + `91d7092` (coverage-gap confirmation and its test). Final product commit **`91d7092`**, `product_code_digest adfd1988c78e9f1856ecc931041040864edc2957a9a82939044439887282c893`, `governed_state_digest` unchanged (`4981437f…227d`) |
| Binary under test | `target/release/gov` at `91d7092`, SHA-256 `37fab1175b85edd141496977e7a89f94544958bfcf501f1dd5a0d6c3e3ae0106` (base binary `7095d188…0332`) |
| Class | **BC-P2-22 — `REPAIRED_CLAIMED`** |
| Integration points | 20 routed IPs: 20 `DONE` (one of them, ws06 IP-8, needed no product change and has a regression test instead), 0 `OBSOLETE` ([`claims.yaml`](claims.yaml)) |
| Regression | `cargo test --lib` **151 / 0** (base 146); `cargo test --test certification` **100 / 0**; R1 held-out suites at their recorded baselines (the AR-0033 `hv_a::a1` size pin aside: 107 files / 1510 functions, 0 violations); rustfmt clean on every touched file; no build warning |
| Probes | 48 audit-of-record runs re-run unedited against the base binary and the repaired binary: **27 FAIL→PASS, 0 PASS→FAIL** (367 PASS→PASS, 113 FAIL→FAIL); builder probe 51/51 |
| Owner decisions | none raised |

These are builder claims. Everything here is regression evidence (Contract v3 O3). No class is claimed accepted.

---

## 0. What changed, in one view

| Area | Files (all WS-2-owned, or declared additive hot-spot edits) |
|---|---|
| W7 orphan detection and remediation (BC-P2-22) | `runtime/src/verification/lineage.rs` (new), family `lineage_orphans` |
| Reporting side of other workstreams' checks | `runtime/src/verification/reporting.rs` (new); `runtime/src/verification/mod.rs` (`run_family` hooks, `audit_with`); `runtime/src/verification/families_ext.rs` (gate wording) |
| T2-bound evidence and the T2 currency class | `runtime/src/verification/currency.rs` (`T2_BINDINGS`, `honoured`, `latest_green`, `Currency`); `runtime/src/verification/product.rs` (seal, honour) |
| Scheduler and tier contract (unchanged signatures) | `runtime/src/scheduler/mod.rs` (`qualification_run`, `QualificationRun`, `Trigger::qualification`, `RunOptions.qualification`, `failure_memory_summary`, two key extras); `runtime/src/scheduler/catalogue.rs` (6 families, 3 doctor checks, 2 extras, duties) |
| Doctor | `runtime/src/doctor.rs`: D015 (names), D017 (store path), D019 (presentation rule), **D032** (installation authenticity), **D033** (T2), **D034** (failure memory) |
| Exit code | `runtime/src/error.rs`: `HEALTH_HARD_BLOCK` → 4 |
| Comment | `runtime/src/skills.rs` (O-6) |
| Policy / schema | `framework/policies/TEST_POLICY.yaml` (six families appended to `governance_families`; no new key); `framework/schemas/audit.schema.json` (x-schema-version 1.2.0: `os_binding`, `remediation`, `qualification`, `findings[].orphan`) |
| Hot spots (additive only; 0 lines removed) | `cli/src/main.rs`: `HealthCmd::Qualify` variant, its arm, its `g0_label` arm `"health qualify"`. `runtime/src/orchestration/control.rs`: `g("health qualify", "record_audit", Write)` |
| Certification tests (behaviour change, §5.2) | `tests/certification/{brownfield,migration,repair2}.rs` |

## 1. BC-P2-22 — orphan / dead-output and unexplained-output detection

**Requirement** (repair-delta §1 BC-P2-22; Contract v3:1138-1144 W7; W12 G5 "audits end-to-end lineage and orphan
states", :1191). Each W7 orphan class is detected **by name** and turned into governed investigation/remediation work,
never silent deletion. Finding A0-W7-01 (HIGH): no surface named an unconsumed output, a requirement without an
implementation/test path, unconsumed research, an unjustified test or unjustified code; only dangling edges and an
anonymous orphan count; no remediation.

**What changed.** `verification::lineage::detect(p, store, db)` computes every W7 class from the governed records'
canonical edges (`graph::lineage::record_edges`, WS-4), version control and — where available — the code graph of the
derived index. Records the remediation itself creates (`generated_by: health:lineage_orphans`) are removed from the edge
view, so remediation never counts as a consumer, implementation, test or justification and never hides an orphan.

| W7 bullet | kind | detected when | severity |
|---|---|---|---|
| :1139 completed output with expected consumers, no actual consumer | `unconsumed-output` | a current record declares `consumers` and no other live record consumes it, or a declared consumer does not exist (architecture records count every live task as a consumer — the compiler delivers them implicitly) | medium (ACTIVE), low otherwise; low when consumed but a declared consumer does not declare it |
| :1140 requirement/spec without downstream implementation/test path | `spec-without-downstream-path` | a live requirement or scenario that no task, report, change or code reaches, and that no test obligation or test file validates (one hop through the scenarios it is validated by) | **medium** when implementation work of its feature is already DONE (a delivery gap); low otherwise (unplanned work is backlog, not a defect) |
| :1141 research expected to feed a decision, never consumed | `unconsumed-research` | complete research/experiment output (has a conclusion/result) that no decision or change cites (`derived_from`, any edge, or `evidence_refs`/`evidence`/`sources`) | medium when the decision it declares it feeds was decided without it, or does not exist; low when it names no decision and none consumes it |
| :1142 acceptance test without requirement/scenario | `unjustified-acceptance-test` | an acceptance-level test obligation (family acceptance/scenario/system, or listed as `acceptance_tests`) linked to no live requirement or scenario (directly, or via a task that declares both) | medium; low for a non-acceptance test obligation linked to nothing governed |
| :1143 implementation/code with no active requirement/decision/spec justification | `unjustified-code` | a `source`- or `test`-class file (repository contract) that no live governed work produced with a trace to a current specification record, no current specification names, no COMMITTED CIT wrote (`execution.propagation.touched`), no justified file imports or calls, and that is not in the governance baseline | medium |

The **governance baseline** is the tree at the commit that first recorded `governance/framework.lock`, the adoption A0
commit, and every path the adoption migration moved existing content to (`migration-ledger.jsonl`, applied rows). Code in
it is adopted as it was: it is disclosed once as a LOW finding ("N source/test file(s) predate governance … not yet linked
to an active requirement/decision/spec"), never reported as unexplained output. Without version control the baseline is
unknowable and code is not judged (stated in the family detail).

**Remediation (:1144).** `lineage::generate_remediation` creates **one investigation task per orphan** that has none:
`READY`, class `validation`, designated role `change-controller` (linking or retiring an orphan is a change), scope
`spec/**`, `production_merge_allowed: false`, `investigates: {kind, subject, key, path, detected_by, detected_at}`,
`provenance`, and an `AFFECTS` relation to the subject (linked work; `AFFECTS` is not a consumption/implementation/test
edge). The key is `W7-<16 hex>` of kind and subject, so generation is idempotent across runs and machines. It runs only
when a run may persist evidence (not `--no-persist`, not a G0 re-evaluation) at G4-G6 with the family selected
(`gov audit`, `gov health run`, host G5 tier runs; never the G2 close gate); it runs **before** the suite, so the evidence
written is current for the state that includes the new tasks, and it refreshes the index for them. It respects
FREEZE_WRITES/PAUSE (nothing created, reason returned). Nothing is ever deleted. Each orphan finding carries its
`orphan` block (kind, subject, key, Contract line, remediation, detail) and, once generated, `remediation_task`.

**Product check and tier.** Family `lineage_orphans` (catalogue: deps `@records` + `@files`, extras `LiveIndex` and
`GovernanceBaseline`, in-process, double-run, cacheable, tiers G4/G5/G6, warning semantics). `gov audit` and
`gov health run` own it; the family detail carries per-kind counts, subjects and keys (the W11 orphan metrics of round 3
read them).

**Probes re-run** (zeta-r `W07-orphan-detection.py`, unedited; base binary vs repaired binary):

| Line | Before | After |
|---|---|---|
| W7-o1-expected-consumer-not-consuming | FAIL | PASS |
| W7-o1-expected-consumer-missing | PASS | PASS |
| W7-o2 / W7-o2b requirement without impl/test (feature link only) | FAIL / FAIL | PASS / PASS |
| W7-o3 / W7-o3b research never consumed | FAIL / FAIL | PASS / PASS |
| W7-o4 / W7-o4b acceptance test without requirement (feature only) | FAIL / FAIL | PASS / PASS |
| W7-o5-unjustified-code | FAIL | PASS |
| W7-o6-orphans-produce-governed-remediation | FAIL (tasks 1→1) | PASS (tasks 1→10: one per orphan) |
| W7-o6-no-silent-deletion, W7-orphan-count-surfaced | PASS | PASS |
| **total** | **3 / 12** | **12 / 12** |

Builder probe `WS02-r2-supplementary.py` W7 group (18 checks, 18 PASS) adds negative controls the audit probe lacks: an
output its consumer declares, a requirement a task governs and a test validates, research a decision cites through
`evidence_refs`, an acceptance test that tests a requirement, and baseline code are **not** reported; `--no-persist`
creates nothing; a second audit creates nothing and still reports every orphan; remediation leaves the index fresh;
code a closed task's report produced with a requirement trace is justified; and once implementation work of the feature
is DONE the untouched requirement becomes medium.

**Tests added.** `verification::lineage::tests::each_record_level_w7_class_is_named_and_linked_records_are_not`.

**Limits.**
- Detection is structural: a record that declares a link is linked; whether the linked work really implements it is the
  receipt contract's business (W5, WS-4/WS-5).
- Research "complete" means it carries a conclusion/result; WS-10's completeness predicate (BC-P2-47) should replace it
  (round-3 IP R3-12).
- Unexplained-code detection needs version control for the baseline; supporting-code propagation needs the derived
  index's code graph (both stated in the detail when unavailable).
- Remediation generates the investigation; the event-driven generation engine for every finding source is BC-P2-24
  (WS-5, round 3), which can adopt these tasks by `generated_by`/`investigates.key` (R3-5).

## 2. Integration points routed to this workstream

| IP (origin) | Status | Where / how | Evidence |
|---|---|---|---|
| ws01-12 **IP-1** contract verify at G5/doctor | DONE | family `contract_binding` (G5/G6, cacheable over an `Extra::ContractSource` digest of the seven chain files): `contracts::verify` over the audited repository when it carries the chain, else the checkout `GOV_CANONICAL_ROOT` names; any `CONTRACT_*` error is HIGH and refuses `release.build`. Not applicable (stated) in a consumer project without a checkout. No doctor check was added: the family is the G5 owner | supplementary SUITE.contract, SUITE.contract-mutated (a diverged generated view → HIGH `CONTRACT_GENERATED_VIEW_DIVERGED`) |
| ws01-12 **IP-4** G6 entry validates oracle and score report | DONE | `scheduler::qualification_run(p, &QualificationRun)` and `gov health qualify --kind --oracle --report [--public-suite] [--repository] [--run-id]` (G0: Write / `record_audit`). Refuses unless the oracle conforms and is separate from the public suites, the given repositories **and this repository**, and the report conforms and is bound to that oracle; then runs G6 (all checks fresh) and records the qualification on the health result and the governance-suite record. The record carries **no oracle id, digest, fault identity or truth** — only a one-way commitment its custodian can recompute, the report digest and numeric V4 metrics — because it lives in the qualification repository (Contract v3:1062; the separation scan found the first draft's oracle id there). A `FORMAT_SAMPLE` oracle is recorded `counts_as_qualification: false` | supplementary G6.1-G6.4 (+ G6.1b: no trace of the oracle id anywhere in the project after a run) |
| ws01-12 **IP-5** hidden-oracle material is HIGH | DONE | `schema_invariants`: a governed record for which `qualification_oracle::is_hidden_oracle_material` holds (the IP's recipe); `path_map_compliance`: every other repository file carrying the format marker or a hidden-oracle type (`reporting::hidden_oracle_material`) | supplementary SUITE.hidden-oracle; epsilon-r V §B runs `--family schema_invariants` and now reports FM-0001/FM-0002 |
| ws03 **IP-5** `t2::audit` and `gates::unverified` reported, and in the currency key | DONE | family `os_binding_integrity` (G1-G6, never cached) and doctor **D033**; severities (`reporting::t2_severity`): BROKEN in force **high** (refuses `release.build`), BROKEN history medium, an UNSEALED gate in force medium, an UNSEALED approval decision low (legacy or hand-written: disclosed, not honoured), FOREIGN / key unavailable low. New non-file currency class **`t2_bindings`** (digest of `t2::audit`: which T2 records no gov operation on this machine produced as they stand) — a forged or edited record, a clone or a replaced machine key stales green evidence | supplementary T2.1-T2.4, CUR.1 (removing the machine key changes exactly `t2_bindings`); synthesis AC16-X2 `X2-L3xU-suite-detects-forged-approval` FAIL→PASS |
| ws02 **IP-WS02-10** `HEALTH_HARD_BLOCK` → exit 4 | DONE | `GovError::exit_code` (blocked class, API-0002) | supplementary EXIT.1 |
| ws02 **IP-WS02-17** doctor posture/authenticity and plugin checks | DONE | posture: doctor **D032** = `srr::installation::doctor_check` (medium when authenticity is not established, so the doctor verdict is never HEALTHY without disclosing it). Plugins: D028 and `plugin_governance` already consume WS-7's `capabilities::governance::findings`; WS-7 exposes no further API at this base, and whatever WS-7's round-2 work adds to that surface reaches both | supplementary DOC.D032; synthesis `X3a-A2:150xU-no-masquerade` PASS on both binaries (on the base only incidentally, through D021) |
| ws02 **IP-WS02-22** honour only T2-bound green and product-test records | DONE | `audit_with` and `product::run` seal their records (`health:governance-suite`, `health:product-tests`); `currency::latest_green` and `product::latest_records` honour only verified records; D021 names green records that are not honoured; the product-evidence cache digest reads only honoured records | supplementary T2.5-T2.8 |
| ws04 **IP-7** misplaced records, stale links, unconsumed outputs | DONE | `graph_integrity`: misplaced records (W1), stale lineage links (W8) without the completed CITs' own change subjects (`reporting::current_stale_links`), and `blocks` naming no task, each medium and named; unconsumed outputs are W7 (`lineage_orphans`); doctor D015 names dangling edges, orphan records, misplaced records and stale links | zeta-r `W1-b3` FAIL→PASS, `W8-l4` FAIL→PASS; supplementary SUITE.misplaced, SUITE.stale, SUITE.stale-cit |
| ws04 **IP-8** untraceable closed tasks | DONE | `product_traceability` reports `context::receipt::untraceable_closed_tasks`, naming the missing lineage link. Severity follows the close regime: **medium** when the closing report carries `receipt_validation` (closed under the receipt contract, i.e. a bypass); **low** for a pre-receipt / legacy close, which no governed operation can re-trace (disclosed, not a permanent health failure) | zeta-r `W5-c2-…-reported-by-audit` and `W8-l3` FAIL→PASS |
| ws04 **IP-9** `verify_delivery` in `context_reproducibility` | DONE | for every dispatchable task (READY/CLAIMED/IN_PROGRESS/REVIEW): compile its packet (sandboxed) and `context::verify_delivery`; a BLOCKED packet (named missing inputs) is medium, a delivery that does not verify or cannot compile is high | zeta-r `W10-a5` FAIL→PASS, `W12-G5-*` FAIL→PASS; supplementary SUITE.delivery |
| ws04 **IP-10** stable finding ids | DONE | one scheme with ws09-11 IP-1 (below) | zeta-r `W1-b1-audit-finding-id-stable` FAIL→PASS |
| ws09-11 **IP-1** `assign_finding_ids` replaces positional `GF-` | DONE | `audit_with` assigns every finding `migrations::identity::assign_finding_ids` (family, message, path → `GF-<10 hex>`, duplicates `-2`…): the same function the adoption audit uses, so the product has one finding-id scheme; `graph::identity::stable_content_id` remains the general helper for other outputs | supplementary IDS.1, IDS.2 |
| ws05 **IP-2** production-merge findings, dangling blocks | DONE | family `task_contract_integrity` (G2/G4-G6, never cached): `tasks::production_merge_findings` each **high**, refusing `release.build`; dangling `blocks` in `graph_integrity` | delta-r `J2.merge.detected` FAIL→PASS |
| ws05 **IP-7** D017 names the real claims store | DONE | `ClaimsStore::path_for(p)`, shown relative to the root when inside it | supplementary DOC.D017 |
| ws06 **IP-2** coverage check at G1/G5; persisted regression misses; open failures reported | DONE | family `index_content_coverage` (G1/G4-G6) over `memory::coverage::verify`: medium for a confirmed gap in current material, low for archived material only. The reporting side **confirms** each gap by re-checking the artefact's whole content against its chunks with heading markers removed on both sides, because the verifier compares a Markdown heading line stripped of `#` against chunk lines that may hold it with its markers — an artefact of the verifier, recorded in the detail (R3-4). A persisted run whose `memory_retrieval_regression` result is failing records each missed query (`memory::failures::record_heldout_misses`; never under `--no-persist`). Open failures: doctor **D034** (an open tool failure degrades, low; retrieval-miss events are reported) and `gov health status.failure_memory` | supplementary SUITE.coverage, DOC.D034, DOC.status-failure-memory; `index_content_coverage` unit test |
| ws06 **IP-8** index manifest in the currency key | DONE | already satisfied by the round-1 key (class `index_manifest`, whose normalisation keeps each entry's `derivation` key); regression test added | `currency::tests::manifest_normalisation_drops_volatile_fields_only` (derivation assertion) |
| ws08 **IP-1** doctor posture check | DONE | D032 (above) | supplementary DOC.D032 |
| ws08 **IP-2** audit finding for unestablished authenticity | DONE | family `installation_authenticity` (G1/G4-G6): **low** on an unprovisioned (bootstrap, OWNER-DECISION-P2-0002 item 2) machine — disclosed; governance evidence is not a release-authenticity claim — **medium** on a provisioned machine that cannot establish it. The doctor verdict carries the stronger consequence (D032) | supplementary DOC.audit-disclosure |
| integration **O-2** D019 wording/semantics | DONE | D019 follows WS-3's rule (presented = owner-signed receipt or answer): a pending gate **never rendered** exists only in files and fails (INV-008); a gate rendered to the human channel and awaiting the owner's receipt or answer is reported ("not yet evidenced as presented") without failing; `human_gate_integrity` wording aligned | supplementary DOC.D019a/b; delta-r `L3.b1.4` PASS; epsilon-r U SLO-7: the five rendered gates no longer fail D019, the unrendered one does |
| integration **O-6** stale `skills.rs` comment | DONE | comment names the L3 declaration | — |
| integration fix `811317b` (trust anchor via `srr::verifier::trusted_root`) | kept | `currency::machine_trust_state` unchanged; AR-0031 `hx_a::a4` passes | R1 re-run §5 |

## 3. Behaviour changes other workstreams and verifiers will see

- **Generated work.** A persisted G4-G6 run creates READY investigation tasks (designated `change-controller`) for new
  orphans; they appear in `task list`/`task dag`. A later run creates none for the same orphan.
- **Doctor is DEGRADED on every unprovisioned machine** (D032) — BC-P2-36's determined requirement and AC16-X3 `X3a`.
  Consequently adoption A11 cannot say `ADOPTED_HEALTHY` on an unprovisioned (bootstrap) machine (§5.2).
- **Evidence honoured only on the machine that sealed it.** After a clone or on a fresh machine, green governance and
  product-test evidence must be re-established (`gov health run`, `gov verify product`); D021 names what is not honoured.
- **New findings can take a suite out of HEALTHY**: stale lineage links, misplaced records, W7 delivery gaps and
  contract mismatches, untraced work closed under the receipt contract, confirmed coverage gaps in current material, an
  unsealed gate in force (medium); tampering in force, hidden-oracle material, production merge (high).
- **Currency key**: a new class `t2_bindings`; the first run after upgrading re-establishes currency (the runtime identity
  changes anyway).
- **Finding ids** are content-derived (`GF-<10 hex>`), shared with the adoption audit.
- **`HEALTH_HARD_BLOCK` exits 4.**
- **Cost.** A full suite does more (six families; per-task packet compilation for dispatchable tasks; lineage over git);
  `audit --no-persist` on a small project measured 2.3 s → 3.0 s on a heavily loaded machine (load average ≈ 70 on 20
  cores during this run). The certification suite took 207 s (the integration builder recorded 191 s).

## 4. Probes re-run (audit of record, unedited)

`evidence/run-audit-probe.sh <label> <tree> <mode> <family> <probe…>` runs each probe unedited from a tree against that
tree's `target/release/gov`, writing only into this evidence directory. The **base** tree is a `git archive` export of
`843d79c` with the base binary (`scratch …/p2ar0023/base-tree`, committed into a local git repository only so the
synthesis X3 minting helper can `git archive` it); the **after** tree is this worktree at `91d7092`. `shim` mode
reaches the same unedited probe through the round-1 integration builder's evidence adapter (P2-AR-0022
`gov-owner-channel-shim.py`, used unedited), for probes that predate WS-3's role and human-channel changes; both
binaries are measured the same way. `compare_probes.py` pairs every marked verdict line; `normdiff.sh` gives the
normalised diff of unmarked probes (`evidence/normdiff/`), each reviewed.

**48 runs (36 direct, 12 through the adapter): 27 FAIL→PASS, 0 PASS→FAIL, 367 PASS→PASS, 113 FAIL→FAIL**
(`evidence/COMPARE-probes.out`). Tracebacks: 15 runs on each binary, the same probes (role/human-answer paths WS-3
removed; they run to completion through the adapter).

| FAIL→PASS line | Owner of the flip |
|---|---|
| zeta-r W7-o1, -o2, -o2b, -o3, -o3b, -o4, -o4b, -o5, -o6 (9) | BC-P2-22 (§1) |
| zeta-r `W1-b3-noncanonical-location-flagged` (direct and adapter), `W8-l4-stale-link-to-superseded-detected` | ws04 IP-7 |
| zeta-r `W5-c2-untraceable-implementation-reported-by-audit`, `W8-l3-missing-task-to-code-link-detected` | ws04 IP-8 |
| zeta-r `W10-a5-product-tests-delivery-against-declaration`; `W12-G5-audits-superseded-consumption`, `W12-G5-audits-end-to-end-lineage`, `AC16-W12xO5-health-state-reflects-superseded-consumption` | ws04 IP-9 / IP-7 (the G5 audit now names a DONE task's consumption of a superseded requirement as a stale lineage link, medium) |
| zeta-r `W1-b1-audit-finding-id-stable` | ws04 IP-10 / ws09-11 IP-1 |
| delta-r `J2.merge.detected` | ws05 IP-2 |
| synthesis `X2-L3xU-suite-detects-forged-approval` (direct and adapter) | ws03 IP-5 |
| **incidental — not claimed for their classes:** delta-r `J1.b.audit` (BC-P2-47: the line only checks that findings name the research records; they are named by W7 *consumption* findings, not by completeness); zeta-r `W6-s7-stale-evidence-surfaced(direct)` (BC-P2-04: the dependent tasks are named by *untraced-implementation* findings, not by staleness propagation); zeta-r `W11-m1`, `W11-m8` (BC-P2-23: the probe matches metric-like key names in the new family details; the W11 metrics are round 3); synthesis `X1-UxO5-health-reflects-invalid-completed-work` (BC-P2-44: doctor is DEGRADED because D032 discloses the unprovisioned probe machine, not because health reflects the invalid completed work) | — |

Unmarked probes (normalised diffs): epsilon-r `O5-scheduler-requirements` — 31 families per run, doctor DEGRADED by
D032; `O2-governance-families` — the new families' findings on the probe's own faults (unexplained `src/creds.rs`, a
READY task with a missing input); `O4-suite-currency` — §A-§E identical, §F shows the generated investigation tasks as
runnable and the G5 audit DEGRADED (the feature's DONE work skipped REQ-0001/SCN-0001: W7 delivery gaps); `O1` — a
test obligation outside its canonical directory is now named (W1); `U-slos-and-healthy` — D032 everywhere, D019 per
§2 O-2; `V-oracle-format-and-contract-views` §B — FM-0001/FM-0002 reported HIGH by `schema_invariants`;
gamma-r `FRESH-invalidation`, `H2H3-readiness`, `I1I2-tasks`, `E4-claims` and alpha-r `FRESH-invalidation` (direct and
adapter) — identical apart from hashes, claim-race order and one source line the I1I2 grep now also finds.
Currency (BC-P2-03) held on every probe that measures it: zeta-r FR 26 PASS / 0 FAIL on both binaries, beta-r FRESH
10/10, delta-r FRESH 12/1 through the adapter on both (the one FAIL is the documented adapter artefact `F.impl.1`),
alpha-r FRESH unchanged, synthesis `X1-O4-green-stale-after-direct-spec-change` PASS→PASS.

## 5. Regression and preservation

### 5.1 Product regression (at `91d7092`)

| Suite | Result | Evidence |
|---|---|---|
| `cargo test --lib` | **151 passed, 0 failed** — base 146 + 5 new (`currency::non_file_classes_are_keyed_and_never_file_classes`, `lineage::each_record_level_w7_class_is_named_and_linked_records_are_not`, `reporting::t2_severity_separates_…`, `reporting::a_completed_change_transaction_is_not_a_stale_link_…`, `reporting::a_coverage_gap_is_confirmed_unless_…`); one existing currency test extended (derivation keys) | `evidence/regression/cargo-test-lib.out` |
| `cargo test --test certification` | **100 passed, 0 failed** (207 s; includes `section6::*`, `srr::*`, `ws03::every_cli_command_label_is_classified_by_g0`) | `evidence/regression/cargo-test-certification.out` |
| rustfmt `--check` on every touched Rust file | 0 hunks each; release build: 0 warnings; hot-spot files: 0 lines removed | `evidence/regression/rustfmt-and-hotspots.out` |
| Builder probe `WS02-r2-supplementary.py` | **51 / 51** (W7 18, T2 8, CUR 1, IDS 2, EXIT 1, G6 5, DOC 7, SUITE 9) | `evidence/WS02-r2-supplementary.{py,out}` |

### 5.2 Certification tests changed, and why

BC-P2-36 (determined requirement, AC16-X3 `X3a`): an installation whose authenticity is not established cannot yield a
HEALTHY verdict without disclosing it; D032 therefore fails on every **unprovisioned** test machine, which is what the
certification harness uses until WS-8's round-2 change provisions a throw-away root (OWNER-DECISION-P2-0002 item 3).
Three assertions depended on a HEALTHY doctor on such a machine:

| Test | Change | Why it is not a weakening |
|---|---|---|
| `repair2::genuine_412_consumer_updates_through_413_to_414_and_rolls_back_with_ledger` | the allowed doctor failures after the update chain are D021 **and** D032 **only when** D032's own posture is `UNPROVISIONED` | every other check must still pass; D032 is the disclosure BC-P2-36 requires |
| `brownfield::brownfield_adoption_end_to_end`, `migration::path_migration_with_rollback_and_memory_rebuild` | A11 may also be `NOT_ADOPTED_HEALTHY` **only when** every adoption criterion holds, the audit is HEALTHY, and the only failing doctor check is D032 disclosing an `UNPROVISIONED` posture (`adopted_but_for_unprovisioned_posture`) | the strict `ADOPTED_*` verdicts apply unchanged on a provisioned machine; every property the tests assert is still asserted |

After WS-8 provisions the harness, these relaxations become dead branches and can be removed (R3-7).

### 5.3 R1 held-out suites (P2-HO-0020 item 7: a private path measuring this tree)

`evidence/r1-heldout/run-r1-heldout.sh` — the integration builder's runner with only its labels, scratch variable and
`CARGO_BUILD_JOBS=2` changed (`evidence/r1-heldout/runner-diff-vs-P2-AR-0022.out`) — copies each suite byte-identically
(`cmp` lines in the output) into a **private, run-named** scratch (`…/p2ar0023/r1-P2-AR-0023-private-91d7092`) whose
`wt/srr1-r1-verify*` links point at this worktree only. HEAD `91d7092`, 0 product files differing.

| Suite | Recorded baseline | This tree |
|---|---|---|
| AR-0027 | 26 / 3 (`b1`, `b2`, `d3`) | **26 / 3**, same tests |
| AR-0029 | 26 / 2 (`b3`, `b6`); `ho_f_preservation` does not compile | **26 / 2**, same; `ho_f` does not compile |
| AR-0031 | 27 / 7 (`a1`, `a5`, `a8`, `b6`, `c2`, `c3`, `d2`) | **27 / 7**, same tests (`a4` passes: the currency key still reads the anchor only through `srr::verifier::trusted_root`) |
| AR-0033 | 31 / 0 | **30 / 1**: `hv_a_derivation::a1` only — its pins (84 files / 740 functions) against this tree's **107 files / 1510 functions** (the integrated base measured 105 / 1457; this run adds `verification/lineage.rs` and `verification/reporting.rs`) |

AR-0033's census, run as the labelled copy `evidence/r1-heldout/hv_a_derivation.a1-unpinned.P2-AR-0023.rs.txt` (its
`diff` against the held-out file — exactly the two size assertions — is in the output), and AR-0033's own `derive.py`
(ROOT line only substituted, all three splitter configurations): **0 violations in every §6 activity**
(human_gate_create derived 44 / writers 39 / exempt 1; human_gate_approve 1/1; release_certification 1/1;
trust_policy_mutation 8/1; privileged_plugin_acquisition 10/2; floor_lower_or_reset 3/1;
present_below_floor_release_as_current 1/1). The one additional derived/writer path is `lineage::remediate` →
`records::save_record` (task records), which conforms. `tests/certification/section6.rs` is green. No file under
`runtime/src/srr/**`, `kernel*.rs`, `lock.rs`, `init.rs`, `update.rs`, `release.rs`, `recovery.rs`, `records.rs`,
`tools.rs` or `capabilities/**` changed. The intermediate run at `1e75f4b`
(`r1-heldout-ws02-r2-1e75f4b.out`, 107 files / 1509 functions) gave the same results.

## 6. Tier contract

Unchanged for hosts: `scheduler::guard(p, op, &paths)`, `scheduler::tier_run(p, Tier, Trigger)`,
`verification::close_gate(p, &task, &report, &touched, force)`, `scheduler::run_suite(p, &RunOptions)`,
`catalogue::ops`. Additions: `RunOptions.qualification: Option<Value>` (set by `RunOptions::new` to `None`; only the G6
entry uses it), `Trigger::qualification(kind, run_id)`, `scheduler::qualification_run`, `scheduler::QUALIFICATION_KINDS`,
`scheduler::failure_memory_summary`, and `scheduler::status` → `failure_memory`. `gov health checks` now lists 65 checks
(31 families + 34 doctor checks) and the input class `t2_bindings` (`evidence/gov-health-checks.json`).

## 7. Integration points for round 3 (new)

| ID | Owner / file | Change | Why |
|---|---|---|---|
| R3-1 | WS-4 `runtime/src/cit/mod.rs` (rollback, the "mark the approval decision REJECTED" block) | re-seal the decision after setting it REJECTED (`t2::seal_record(d, "cit rollback")`), as WS-3's `revoke` does | today the OS's own rollback leaves a decision BROKEN, which `os_binding_integrity` must report as tampering (medium, history); seen in `repair::smaller_findings_regressions` |
| R3-2 | WS-4 `graph::lineage::stale_links` | exclude a completed (COMMITTED / ROLLED_BACK / REJECTED) CIT's links to the records it changed | the reporting side filters them (`reporting::current_stale_links`); the detector should not produce them |
| R3-3 | WS-4 `records.rs` relation fields | give decision `evidence_refs` (and similar citation fields) a relation edge (e.g. `DERIVED_FROM`) | research consumption becomes a graph fact; `lineage` reads the field directly meanwhile |
| R3-4 | WS-6 `memory/coverage.rs` / `memory/chunking.rs` | normalise heading markers on **both** sides in `uncovered_lines` (or hold headings without markers consistently); list every uncovered line | the verifier reports held heading lines as gaps; the reporting side confirms gaps meanwhile and records the artefacts in the detail |
| R3-5 | WS-5 BC-P2-24 engine | adopt the W7 investigation tasks (`generated_by: health:lineage_orphans`, `investigates.key`) and extend generation to the other finding sources | one event-driven generator |
| R3-6 | WS-1 `tests/governance/capability-evidence-map.yaml` (BC-P2-02) | owners: W7 → `lineage_orphans` (G4-G6) + remediation; BC-P2-09 detection → `os_binding_integrity`, D033; BC-P2-36 → D032, `installation_authenticity`; BC-P2-01 at G5 → `contract_binding`; BC-P2-25 → `index_content_coverage`; Contract v3:614 → `task_contract_integrity`; W1/W8 → `graph_integrity`; W5 → `product_traceability`; W4 → `context_reproducibility`; G6 → `gov health qualify` | AC-10 evidence owners |
| R3-7 | WS-8 (harness) → any | once the harness provisions a throw-away root, remove `adopted_but_for_unprovisioned_posture` (brownfield.rs, migration.rs) and the D032 filter (repair2.rs) | the strict assertions then hold unchanged |
| R3-8 | WS-2 round 3 (BC-P2-23, BC-P2-44) | W11 metrics from `lineage_orphans` detail (orphan recall / false positives), requirement→code/test coverage, delivery accuracy from `context_reproducibility.delivery`; SLO thresholds and the HEALTHY conjunction | round-3 classes |
| R3-9 | WS-9 `adopt::a11_audit` | name the unestablished installation authenticity as the reason when D032 is A11's only doctor failure | A11 now says `NOT_ADOPTED_HEALTHY` on a bootstrap machine; the report should say why |
| R3-10 | WS-3 / docs owner | document `gov health qualify`, doctor D032-D034, the new families and the T2-honoured evidence rule in `docs/COMMANDS.md` / `docs/ARCHITECTURE.md` | documentation |
| R3-11 | WS-7 (+ WS-3 `t2::audit`) | when the plugin registry is sealed (ws03 IP-6), include registry entries in `t2::audit` so `os_binding_integrity` and `t2_bindings` cover them | T2 coverage of the registry |
| R3-12 | WS-10 → WS-2 | expose the research/experiment completeness predicate (BC-P2-47/48); `lineage::unconsumed_research` should use it instead of "has a conclusion/result" | one completeness rule |

## 8. Owner-decision questions

None. The severity choices above (W7 severities, untraced work by close regime, the bootstrap disclosure being low in
the audit and failing in doctor, T2 severities) are determined by the cited sources and owner decisions
(OWNER-DECISION-P2-0002; BC-P2-36; D-0007 rule 2) or are the repair role's to make, and each is stated with its reason.

## 9. Limits and what was not done

- BC-P2-07 (tier duties), BC-P2-23 (W11 metrics) and BC-P2-44 (SLO thresholds, HEALTHY conjunction) are round 3 and were
  not started; no host call site was wired (the hosts are wiring against the unchanged tier contract in parallel).
- The W7 checks judge declared links, not the quality of the linked work.
- The coverage-gap confirmation compares the verifier's expected content with chunk lines; the root cause is WS-6's (R3-4).
- G6 records a qualification run; it does not execute synthetic repositories, chaos, soak or hidden tests (Phase 4).
- Evidence outputs contain absolute scratch paths of this run.

## 10. Evidence index (`evidence/`)

| Path | Content |
|---|---|
| `run-audit-probe.sh` | runs audit-of-record probes unedited against a tree (direct or through the P2-AR-0022 adapter) |
| `before/`, `before-shim/` | base binary (`843d79c` export) — 36 direct, 12 adapter runs |
| `after/`, `after-shim/` | repaired binary (`91d7092`) — the same 48 runs |
| `compare_probes.py`, `COMPARE-probes.out` | marked verdict lines paired (27 FAIL→PASS, 0 PASS→FAIL) |
| `normdiff.sh`, `normdiff/` | normalised diffs of the unmarked probes |
| `WS02-r2-supplementary.py`, `.out` | builder probe, 51/51 |
| `gov-health-checks.json` | the check catalogue and input classes |
| `regression/` | `cargo test --lib` (151/0), `--test certification` (100/0), rustfmt and hot-spot diff |
| `r1-heldout/` | runner and its diff against the P2-AR-0022 runner, labelled unpinned `hv_a` copy, final run `r1-heldout-ws02-r2-final.out` (at `91d7092`) and the intermediate run at `1e75f4b` |

## 11. Process disclosures

- Model Claude Opus 5 (1M context), `claude-opus-5[1m]`. No sub-agents; the product owner was not contacted; no session
  or agent transcripts, task-output stores or user auto-memory were read. Long commands ran in the foreground.
- One shell command that deleted an intermediate evidence file (`rm -f`) was denied by the permission system; it was
  not retried, and the intermediate file stays in `evidence/r1-heldout/`, labelled as such above.
- Development iterations found three defects of this run's own draft, each fixed before the final evidence: the probe
  counted tasks from `task list` (which omits fields) — corrected to read the records; the first G6 record carried the
  oracle id and digest inside the qualification repository — now a one-way commitment only; the first coverage finding
  reported WS-6's heading-marker artefact as a gap — now confirmed before reporting. The final probe, regression and R1
  runs are all at `91d7092`.
