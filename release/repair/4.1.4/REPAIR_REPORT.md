# Repair report — agentic-engineering-os 4.1.4 (second repair iteration, after the rejection of 4.1.3)

Written for: the independent verifier re-verifying the candidate, and the product owner.

| | |
|---|---|
| Rejected candidate | 4.1.3 at commit `26ab5b6eb111d573f8686bc4f4b1dfc20539f45e` (tag `v4.1.3-rc1`) — verdict OS_RELEASE_CANDIDATE_REJECTED (`release/verification/4.1.3/INDEPENDENT_REVERIFICATION_REPORT.md`, `VERDICT.md`) |
| Repair branch | `release/4.1.4-rc1` (branched from the verifier's commit `9cb05d8` on `release/4.1.2-rc1`; nothing rewritten, nothing merged to `main`) |
| Repair code commit | `REPAIR_CODE_COMMIT` |
| Candidate commit | `CANDIDATE_COMMIT` (adds `release/releases/4.1.4/`; tag `v4.1.4-rc1`) |
| Release version | 4.1.4 — kernel payload changed (POLICY_PRECEDENCE, TOOL_POLICY.plugins, schemas, roles/authority map, migration) → new immutable PATCH release; 4.1.3 untouched and REJECTED |
| Migration chain | `M-4.1.1-4.1.2` → `M-4.1.2-4.1.3` → `M-4.1.3-4.1.4`; supported_from 4.1.1 / 4.1.2 / 4.1.3; exercised from a genuine 4.1.2 payload through 4.1.3 to 4.1.4 with two ledgered rollbacks (`repair2::genuine_412_consumer_updates_through_413_to_414_and_rolls_back_with_ledger`) |
| Certification | **pending** — READY_FOR_INDEPENDENT_REVERIFICATION; the implementer has not certified anything |

Verifier artefacts (`release/verification/4.1.3/**`, `release/verification/4.1.2/**`, both harnesses, both released
`kernel/` payloads) were not modified. Both harnesses were rerun byte-identical (`GOV_VERIFIER_OUT` redirected;
harness v2 with a 4.1.2 binary built from `8ad06be` in a detached worktree). No verifier-authored test was weakened,
rewritten, bypassed or special-cased. The only release artefact edited is the 4.1.3 manifest certification block,
transcribed verbatim from the verifier's `VERDICT.md` at the verifier's explicit request (kernel payload and
`file_hashes` untouched; `gov release verify release/releases/4.1.3` still ok).

## 1. Totals

| Suite | Result |
|---|---|
| `cargo build --release` (clean clone) | CLEAN_BUILD |
| Rust unit tests (gov-runtime) | UNIT_TOTAL |
| Certification suite (7 fixtures + architecture + 17 repair tests for 4.1.2 findings + 9 repair tests for 4.1.3 findings) | CERT_TOTAL |
| Python plugin tests | PY_TOTAL |
| First verifier harness, unchanged (`release/verification/4.1.2/heldout/harness.py`) | HV_TOTAL |
| Second verifier harness, unchanged (`release/verification/4.1.3/heldout-new/harness_v2.py`) | NV_TOTAL |
| rustfmt (`cargo fmt --all -- --check`) | FMT_RESULT |
| Clippy (`cargo clippy --workspace --all-targets`) | CLIPPY_RESULT |
| `gov release verify release/releases/4.1.4` | RELEASE_VERIFY |
| Working tree at the candidate commit | TREE_STATUS |

Evidence: `docs/EVIDENCE.md`, `release/evidence/`, `release/verification/4.1.2/heldout-rerun-4.1.4/`,
`release/verification/4.1.3/heldout-new-rerun-4.1.4/`.

## 2. Preserved repairs (first verification, independently confirmed)

C1 replaceable query/index embedding · C2 plugin-host large responses · H1 mixed-dimension detection · H2 persistent
claims · H3 L0–L5 authority · H4 mutation scope · H5 sensitivity/indexing · H6 destructive-migration gate records ·
H7 reranker hook + benchmark/selection. All `repair.rs` tests still pass and the first harness rerun is unchanged
except HV-08b (by construction, accepted by the second verifier). H3/H5 are no longer nullifiable by the overlay
(H-N1) and H4 is no longer self-attested (M-N4).

## 3. Findings of the re-verification — root cause, invariant, change, tests, residual risk

| ID / severity | Root cause (reproduced) | Violated invariant | Implementation change (components) | Builder regression test | Original independent test after repair | Adjacent negative tests | Residual risk |
|---|---|---|---|---|---|---|---|
| **C-N1** CRITICAL — CIT approval without an answered gate; decline executes; fabricated `human_approved` | `cit::approve` only checked "gate presented", never the answer; `execute` checked `gate_status == ANSWERED` without the option; approve fabricated a decision record with `human_approved: method == "human"` from the caller flag | INV-008 / INV-011, framework §47.2/§52: human approval derives only from an authoritative recorded gate response | `cit/mod.rs`: `authoritative_gate()` (gate bound to the CIT, presented, ANSWERED with A, ACTIVE decision derived from the gate) used by `approve` and re-run by `execute`; approval object records gate, decision, answerer, kind, time, presenter, recorder; method derived from the answer kind (`APPROVAL_METHOD_MISMATCH` if the caller claims human on an agent answer); auto path only within `auto_approve_max_radius` with `human_approved: false`; `gates::answer` marks the CIT REJECTED on any non-A option and removes stale approvals; `gates::revoke` (new, L4) withdraws a gate, its decision and any derived approval; `present` records `presented_by`; execution journal carries gate/decision ids | `repair2::cit_approval_derives_only_from_an_answered_gate` | NV-01 → PASS (a, b, c refused; CIT REJECTED after B; nothing written) | unpresented (`GATE_NOT_PRESENTED`), presented-unanswered (`GATE_NOT_ANSWERED`), L3 agent and L1 worker, forged approval object (`execute` → `GATE_NOT_ANSWERED`), decline (`GATE_DECLINED`, REJECTED, execute refused), revoked (`GATE_REVOKED`, CIT back to SIMULATED), re-answered record (`APPROVAL_STALE`), option flipped after approval (`GATE_DECLINED`), auto path `human_approved: false`; NV-13 control still PASS | The acting role is caller-declared (L-N4): a session claiming `--role human` is trusted; documented as the adapter's authentication boundary |
| **H-N1** HIGH — overlay lowers authority levels / empties `never_index_classes` silently | `policy::PolicySet::load` deep-set any `<POLICY>.<key>` from `policy_overrides`/exceptions | framework §21 precedence; INV-006: lower layers strengthen, never weaken | `framework/policies/POLICY_PRECEDENCE.yaml` (kernel: layers, per-key modes immutable/floor/ceiling/additive/shrink_only/strengthen_only_bool/overridable, deny-by-default, `exception_relaxable`); `policy_precedence.rs` (`evaluate`, embedded fallback for older kernels); `policy.rs` records `applied_overrides` (with mode) and `refused_overrides` (with reason), leaves the effective policy unchanged on refusal; exceptions require a decision; doctor D027 (CRITICAL), suite family `policy_precedence`, context-packet layer 3, `gov policy overrides|effective` | `repair2::project_policy_cannot_weaken_constitutional_floors`; unit `policy_precedence::tests` | NV-02 → PASS (L0 denied; restricted excluded and not retrievable; D027 CRITICAL; audit findings) | authority lowering (3 keys), sensitivity weakening (never_index/never_export/secret patterns), human-gate bypass (`must_be_presented_in_chat`, agent radius), change-control (`auto_approve_max_radius` raise, triggers emptied, snapshot off), export (`upstream.approval`), destructive (`archive_mutation`), test-status widening; strengthening applied (raised level, extra class, lowered radius); exception without decision refused, relaxable exception with decision applied; clean overlay HEALTHY | Rule table is kernel data: a future policy key must be classified or it is unoverridable (safe default) |
| **H-N2** HIGH — plugin descriptors are ungoverned executables | `host::discover` accepted any YAML with plugin_id/capability/command; schema unreferenced; no registration, pin, health, role or permission check on `invoke` or pinned use | framework §28–32, TOOL_PERMISSIONS least authority; "no executable capability runs merely because a descriptor exists" | `plugin-descriptor` schema 1.1.0 (identity pattern, `version` required, governance fields, additionalProperties false); `host::discover_all` validates and separates rejected descriptors; `capabilities/governance.rs` (`authorize`: authority floor `TOOL_POLICY.plugins.min_authority`, `approved_roles`, permission classes vs TOOL_PERMISSIONS, elevated permissions need a presented+answered registration gate, health, declared sha256 pin, per-version observed-hash drift → `PLUGIN_PIN_MISMATCH`; `plugin_set`, `register`, `health`, `findings`); every execution path uses the governed set (indexer, retrieval, benchmark, code intelligence, `capabilities invoke` with `execute_plugin` authority); `gov plugins register|list|health`; plugins in the generated Tool/Capability Registry (`tools::plugin_tools`); doctor D028; family `plugin_governance`; `AUTHORITY_POLICY` execute_plugin/register_plugin; D-0005 | `repair2::plugins_are_governed_capabilities_not_arbitrary_commands` | NV-04 → PASS (minimal descriptor rejected; L0 invoke `AUTHORITY_DENIED`; L0 rebuild refused before execution) | malformed, unregistered by L0/L1, pinned-use by L0, content drift, declared-pin mismatch, version bump re-pin, `approved_roles` exclusion, elevated permissions unregistered (`PLUGIN_NOT_APPROVED`), registration by an unauthorised role, registration gate flow, registered plugin still needs the permission class (`PLUGIN_NOT_AUTHORIZED`), health/registry listing; NV-06/10/17 (valid hand-declared plugins for L3/L4 roles) still PASS | Interpreter-only commands (`python3 -m …` without a local file) have no local file to hash: identified by version only, reported as "no local files to pin" |
| **M-N1 / M-N2** MEDIUM — `framework.lock.release_commit` = consumer HEAD; absolute `source` after update | `init`/`adopt`/`update` passed `Project::git_commit()` and `src.to_string_lossy()` | protocol §4/§8, framework §80: the lock identifies the installed release, machine-independently | `kernel::release_commit_for_source` (release manifest next to `kernel/`, embedded build commit from `build.rs`, or the framework checkout's HEAD), `source_label` on every path; lock schema 1.1.0 adds `installed_at_commit`; `lock.rs`, `init.rs`, `adopt.rs`, `update.rs` | `repair2::framework_lock_is_release_identifying_and_portable` | NV-08 → PASS; NV-03 lock defects gone | release dir, canonical checkout, embedded payload, second clone identical, doctor D003 on the clone | Embedded builds outside a git checkout record `unknown` (reported, never a path) |
| **M-N3 / NV-19** MEDIUM — `M-4.1.2-4.1.3` claims a contract tightening it does not perform; upgraded projects index the held-out file | migration carried no overlay op; template change was not migrated | protocol §8 supported migration paths; framework §75D migration integrity | new op `set_overlay_rule`; `M-4.1.3-4.1.4` performs the tightening explicitly and declares `overlay_template_changes`; `gov update` reconciles template defaults (untouched overlay leaves follow the new template, customisations preserved, listed in `overlay_reconciled`); `migrations::framework::check_substance` refuses a NEW release whose migration neither performs nor declares a template change (`MIGRATION_INCOMPLETE`); the shipped `M-4.1.2-4.1.3` keeps its operations exactly and gains a truthful description + `amendments` history | `repair2::genuine_412_consumer_updates_through_413_to_414_and_rolls_back_with_ledger`, `repair2::interface_contract_kernel_yaml_and_migration_substance_are_consistent` | NV-03 → PASS (held-out file not indexed after a 4.1.2 → 4.1.3 update performed by the 4.1.4 binary); **NV-19 remains FAIL by construction**: it reads the immutable 4.1.3 payload (`release/releases/4.1.3/kernel/migrations/M-4.1.2-4.1.3.yaml`, 4.1.3 release notes) which cannot be changed; the same check against 4.1.4 is the builder test above | a migration claiming a contract change without an op is flagged; historical operations unchanged (4 ops) | Reconciliation changes untouched overlay defaults on update; every change is listed and snapshotted for rollback |
| **M-N4 / NV-05** MEDIUM — mutation scope self-attested | `task close` validated only `report.files_changed` | framework §25/§42: mutation manifests are verified against the repository | `tasks::snapshot_tree` at claim (git `ls-files -co --exclude-standard` + sha256; walk fallback), `observed_mutations` at close (diff vs baseline, OS-managed and contract-generated paths excluded), undeclared or out-of-scope observed changes → `MUTATION_SCOPE_VIOLATION` unless CIT-governed (propagation writes now recorded in `touched`); report/checkpoint carry `observed_files_changed` and the baseline | `repair2::task_close_uses_observed_mutations_not_self_attestation` (+ `repair::task_close_enforces_mutation_scope` tightened) | NV-05 → PASS | out-of-scope declared, out-of-scope undeclared, in-scope undeclared, revert then declare; greenfield fixture gained a realistic `.gitignore` | Tasks closed without a claim fall back to `git status`; build outputs must be git-ignored or contract-declared generated |
| **M-N5 / NV-07** MEDIUM — record lost on incremental rebuild after `git mv` | duplicate-id branch treated "same id, different path" as a duplicate before the removal sweep | framework §13 deterministic incremental indexing | `indexer.rs`: same id at a new path whose old path is gone = relocation (old artefact deleted, `moved` reported); a live second path is still a duplicate | `repair2::incremental_rebuild_follows_record_relocation` | NV-07 → PASS | rename within a directory, second relocation, genuine duplicate still reported, freshness fresh, structured query hits | — |
| **M-N6** MEDIUM — API-0001 promises a silent fallback | interface record not updated when C1 was repaired | code/spec agreement inside the canonical repository | D-0005; API-0001 v1.1 with `history`/`amended_by`; `capabilities/PROTOCOL.md`, `fixtures/failure-injection/README.md` | `repair2::interface_contract_kernel_yaml_and_migration_substance_are_consistent` | (source inspection) | — | — |
| **M-N7** MEDIUM — branch/tag provenance | no tags; 4.1.3 on `release/4.1.2-rc1` | protocol §8 release identity | tag `v4.1.3-rc1` at `26ab5b6`; branch `release/4.1.4-rc1`; tag `v4.1.4-rc1` at the candidate commit; manifest `provenance.release_branch/release_tag`; `docs/RELEASE.md` naming rule | `repair2::release_build_reproduces_released_versions_from_their_commit` | NV-16 → PASS (reproduction of 4.1.3 from its recorded commit) | — | — |
| **M-N8** MEDIUM — real 4.1.2 → 4.1.3 path not in the builder suite | only the synthetic 4.1.1 chain was tested | protocol §7 fixtures | `repair2::genuine_412_…` (immutable 4.1.2 payload → 4.1.3 payload → 4.1.4 kernel, rollbacks) | same | NV-03 → PASS | — | — |
| **M-B1** MEDIUM — no shipped/referenced paraphrase-capable candidate, no benchmark record | — | framework §14.3 | D-0006 (candidate classes, why none is bundled), optional `embed_sentence_transformers.py` plugin template (fails closed without the library), research record `spec/research/RES-0001.yaml` from `gov memory benchmark --record` on the greenfield fixture | `repair::benchmark_records_evidence_and_selection_pins_through_decision` | NV-06 still PASS; HV-08b FAIL by construction (accepted) | — | Baseline variants tie on the starter set; NV-06's paraphrase set is the discriminating benchmark |
| **L-N1 / NV-09** LOW — duplicate key in KERNEL.yaml | two `release-manifest` entries | kernel data hygiene | duplicate removed (KERNEL.yaml 4.1.4); strict duplicate-key scan of every kernel YAML in the builder suite | `repair2::interface_contract_kernel_yaml_…` | **NV-09 remains FAIL by construction**: it loads the immutable 4.1.3 payload's `KERNEL.yaml` | — | — |
| **L-N2** LOW — rollback leaves no ledger entry; second rollback re-applies | rollback wrote nothing and never consumed its snapshot | directive §7 | `update::rollback(reason)`: ledger entry (source/target versions, identity, authority level, reason, migrations reverted, resulting lock, verification), `consumed.json`, `SNAPSHOT_CONSUMED`/`SNAPSHOT_MISSING`; CLI `--reason` | `repair2::genuine_412_…` | NV-03 rollback defect gone | second and third rollback | — |
| **L-N3** LOW — `memory select` derives `human_approved` from `--by` | string comparison | human approval never caller-supplied | `benchmark.rs`: derived from the acting role's authority level (L5 = human), `approved_by_kind` recorded | (covered by benchmark test) | — | — | — |
| **L-N4** LOW — self-declared role | design | trust boundary must be explicit | documented in `docs/ARCHITECTURE.md` §4.8 | — | — | — | remains a boundary for adapters |
| **L-N5** LOW — stale docs | — | — | `fixtures/update/README.md`, `docs/FIXTURES.md`, `docs/ARCHITECTURE.md`, `docs/COMMANDS.md`, `docs/RELEASE.md`, `README.md` updated | — | — | — | — |
| **L-N6** LOW — rustfmt divergent; clippy warnings | — | — | `cargo fmt --all` applied to the whole workspace; clippy diagnostics fixed | evidence | FMT_RESULT / CLIPPY_RESULT | — | — |
| **L-N7** LOW — optional verifier identity in the lock | — | — | not implemented (optional per the verifier); the manifest certification block carries the verifier identity | — | — | — | — |
| §11 evidence vocabulary | — | — | `scripts/collect_evidence.sh` reports PASS / FAIL / NOT_AVAILABLE / NOT_RUN / NOT_APPLICABLE and both harness reruns | — | — | — | — |
| §13 policy consumption | — | — | ENFORCEMENT_MAP extended for POLICY_PRECEDENCE, TOOL_POLICY.plugins, new authority classes; `descriptor_schema` and `require_valid_descriptor` classified informational with reasons | `repair::policy_enforcement_coverage_is_complete_and_honest` | — | — | — |

## 4. Verifier tests that cannot change verdict on this candidate (documented, not modified)

- **NV-09** and **NV-19** read the immutable 4.1.3 payload (`release/releases/4.1.3/kernel/KERNEL.yaml`, its
  `M-4.1.2-4.1.3` migration and release notes). The defects are repaired in the 4.1.4 payload and the canonical
  migration file (history preserved, operations unchanged), and the equivalent checks run against 4.1.4 in
  `repair2::interface_contract_kernel_yaml_and_migration_substance_are_consistent`. Changing those verdicts would
  require mutating a released payload, which the directive forbids.
- **HV-08b** stays FAIL with the baseline embedder by construction; the second verifier assessed it as not blocking.
- **NV-03**'s held-out check treats any hit for the bare marker token as a leak. The held-out file is no longer indexed
  on upgraded projects; in addition a single literal-like token (hyphenated / digit-bearing / upper-case marker) is now
  an exact lookup in the retrieval router (no OR-of-subtokens lexical match, no semantic nearest neighbour), so the
  query returns nothing when the literal is absent — a general retrieval rule, not a special case for the test.

## 5. Architecture constraints preserved

Rust-first deterministic core, no Python to operate it (`arch::core_runs_without_any_governed_toolchain_on_path`,
HV-25 PASS); polyglot capabilities behind `gov-capability/1` (v1.1 contract: governance is part of the protocol, the
transport is unchanged); model independence (D-0006: no model in the kernel, pins replaceable and fail-closed);
Git as truth, SQLite as derived state, claims/control outside the rebuilt store; rebuildability (HV-12/HV-30/NV-03
machine-B); kernel/overlay separation (migration touches overlay/lock/generated only; reconciliation is snapshotted
and rolled back with the overlay); independent verification boundaries (verifier artefacts untouched, no
self-certification).

## 6. Records

D-0005 (interface truth / plugin governance), D-0006 (embedding candidate policy), TASK-0011, RPT-0011,
RES-0001, API-0001 v1.1, release notes `release/notes/4.1.4.md`, migration `migrations/M-4.1.3-4.1.4.yaml`,
amended `migrations/M-4.1.2-4.1.3.yaml` (description + history only).
