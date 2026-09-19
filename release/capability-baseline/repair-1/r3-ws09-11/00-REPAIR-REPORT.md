# Repair 1, round 3, WS-9 + WS-11: builder report (run P2-AR-0040)

| Field | Value |
|---|---|
| Run | P2-AR-0040, role `capability-repair`, model Claude Opus 5 (1M context), `claude-opus-5[1m]` |
| Handoffs | P2-HO-0039, with P2-HO-0031 (incl. the availability rule), P2-HO-0020 and P2-HO-0010 |
| Branch / base | `phase2/repair-1-r3-ws09-11` from `53897c1a44157e5af81b176017bc7ded6a63b9cd` (the integrated round-2 tree, `product_code_digest 797da37c…1fe1`) |
| Work commits | `adb9120` (the repair), `16e4c0b` (M-4.1.5-4.1.6 carries WS-10's IP-WS10-16 upgrade note). Report and evidence follow in a separate commit. |
| Product identity at `16e4c0b` | `product_code_digest 4dedf0279de64c5b070103a1efdb219e790e2dd96e60be968161131372ff7225`, `governed_state_digest 8f191e39…948f` (unchanged) |
| Items | WS-6 r2 IP-R2-10 (migration snapshots → BC-P2-31 store); WS-6 r2 IP-R2-11 (template rules delivered through a migration operation); WS-2 r2 R3-9 (A11 states the posture); the WS-9 r2 command-test observation (Contract v3 A3); coordination of `migrations/M-4.1.5-4.1.6.yaml` with WS-8 |
| Claims | §0. Every claim is a builder claim; the evidence is regression evidence only (Contract v3 O3). |
| Owner decisions | None raised (§11). |

---

## 0. Claims

| Item | Status | Product check that owns it |
|---|---|---|
| IP-R2-10 — migration snapshots in the BC-P2-31 store | `REPAIRED_CLAIMED` | `migrations::executor::{snapshot_dir, prepare_store, locate_snapshot, rollback_batch}` (every A6 batch and every rollback, `gov adopt rollback`, `gov recover`) |
| IP-R2-11 — overlay-template changes reach installed projects through a migration operation (migration side) | `REPAIRED_CLAIMED` (migration side; the template content is WS-6's, IP-R3-WS09-1) | `migrations::framework` op `sync_overlay_template` (every `gov update --check/--apply` that crosses 4.1.5→4.1.6); `check_substance` (every `gov release build`; certification `repair2::interface_contract_kernel_yaml_and_migration_substance_are_consistent`) |
| Command-test privilege (Contract v3 A3) | `REPAIRED_CLAIMED` | `migrations::verify::{command_test_refusal, refuse_unpermitted_command_tests, run_tests_file_as}`, `adopt::command_policy`; enforced at A5 approval, A6 (before any batch) and A7 (before any test), and in the runner |
| R3-9 — A11 names the installation posture | `REPAIRED_CLAIMED` | `adopt::verdict_reasons` in `a11_audit_by` (every A11) |
| M-4.1.5-4.1.6 × WS-8 version/payload decision | done on this side; integration point recorded (IP-R3-WS09-2) | the migration record and `check_substance` |

---

## 1. IP-R2-10 — migration snapshots belong to the BC-P2-31 store

### Requirement

Rollback material survives deleting everything the product classifies derived (repair-delta BC-P2-31; Contract v3
B1:188, B3:202, D6:352; A0-D6-01). WS-6 r2 declared the store (`paths::OS_STORES`, `migration-snapshots`) and routed the
writer move to WS-9: `store_path(root, "migration-snapshots")` joined with the batch, and relocate the legacy directory once.

### What changed (`runtime/src/migrations/executor.rs`, `planner.rs`)

- `snapshot_dir(root, n)` is `paths::store_path(root, "migration-snapshots")/batch-<n>`: `.governance-state/migration/batch-<n>`.
- Before a batch writes, `prepare_store` moves a legacy `.governance-runtime/migration/` there once
  (`paths::relocate_legacy`, typed `STATE_LOCATION_CONFLICT` and nothing overwritten if both places hold different
  material) and ensures `.governance-state/.gitignore`. The batch result and `batch.json` record what was moved.
- A rollback (`gov adopt rollback`, `gov recover`, a failed batch) locates the snapshot after the same relocation; a
  legacy snapshot that cannot be moved is **read where it is**, so the rollback stays available (availability rule).
- **Rollback confinement.** A snapshot on disk is content, not authority. `rollback_batch` now restores only files under
  the paths the batch recorded as `touched`, reverses only moves that start from such a path, removes only created files,
  and never writes a protected location (`governance/kernel/**`, `governance/framework.lock`, `governance/trust/**`,
  `.governance-state/**`, `.git`, the derived runtime directory, absolute or `..` paths). Everything else is reported
  under `refused`. Before, a planted `batch-N/files/governance/kernel/…` or `framework.lock` was restored verbatim (the
  root-of-trust review's RV-M1 note on adoption rollback).
- The catalogue's `rollback` text states the new location.

### Tests

- Lib `executor::tests::batch_snapshots_live_in_the_os_store_and_survive_deleting_the_runtime_directory`,
  `a_legacy_snapshot_is_moved_into_the_store_and_still_rolls_back`, `a_rollback_restores_only_what_its_batch_recorded`.
- Certification `migration::path_migration_with_rollback_and_memory_rebuild` now asserts the snapshot is at
  `.governance-state/migration/batch-2`, **deletes the whole `.governance-runtime/`** before `adopt rollback --batch 2`,
  and still gets the byte-identical rollback with nothing refused. Its tree hash excludes `.governance-state/**` (OS
  operational state, like `.governance-runtime/**` already was) — IP-R3-WS09-3 asks the harness owner to make that the
  default.

## 2. IP-R2-11 — template changes delivered to installed projects by a migration operation

### Requirement

WS-6 r2 IP-R2-11: the repository-contract template states the truthful classification (the `.governance-state/**`
operational rule, the registry location, the memory-quality evidence rule, runtime-directory rules that do not match the
legacy store paths, and — O-1 — a rule order under which the specific `spec/` rules decide their paths); WS-9 supplies
the migration operation that delivers it to installed projects; `framework.json` is re-projected. A template change that
reaches new installations must reach installed projects, and only through the migration record (so it is declared,
shown by `update --check`, rollback-safe).

### Why a new operation

The existing operations cannot deliver such a change: `set_overlay_rule` only edits or **appends** a rule (contract
rules are last-match, so position is meaning), nothing removes the blanket `.governance-runtime/**` rule or re-orders
`spec/**`, and `update`'s template-default reconciliation only follows changed leaf defaults. A migration also cannot
read the previous release's templates at install time (the new kernel is installed first, and a chain has no
intermediate payloads), so the operation carries its base.

### What changed (`runtime/src/migrations/framework.rs`, `framework/schemas/migration.schema.json` 1.2.0, `migrations/`)

- **`sync_overlay_template {file, base_release, base}`**: a three-way merge of the project's overlay file with base = the
  previous release's template (carried in the record) and target = the installing kernel's template:
  - what the project never changed follows the new template: values, rules added, rules removed, rule order;
  - what it customised is kept; a rule it added stays before the rule it preceded (an appended override stays last);
    a project that re-ordered template rules keeps its order and gets new rules after their template predecessor;
  - where both changed the same thing, the project's value is kept and the difference is reported
    (`MigrationOutcome.template_conflicts`, `operations[].conflicts`) — never dropped, never silently applied;
  - an overlay that converges exactly gets the template's own bytes (byte-identical to a new installation);
  - dry-run (`gov update --check`) reports the changes (impact radius R4) and writes nothing.
- **`apply` and the substance check share one implementation** of every in-place overlay edit (`edit_overlay`), and
  `apply` writes a file only when it changed (a missing file is no longer created as `{}`).
- **`check_substance` requires delivery, not only declaration.** For every template file a migration delivers (an overlay
  operation, or a `template_reconciliation` declaration), it simulates `gov update` on a project whose file is still the
  previous release's template — the operations in order, then `update`'s reconciliation — and refuses unless the result
  is exactly the new template (`… does not converge … installed and new projects would disagree`, with the differing
  rules). A `sync_overlay_template` base must equal the previous release's template. `not_applicable` and delegations to a
  later migration (`op:… in M-…`, the frozen historical records) are not simulated. `gov release build` refuses a new
  release on these problems; certification `repair2::interface_contract…` applies them to the migrations into the
  current version.
- **`M-4.1.5-4.1.6`** now carries a `sync_overlay_template` for **every** overlay template, each with the exact 4.1.5
  template as base (verified against `release/releases/4.1.5/kernel/overlay-templates/`). Whatever template change the
  release carries (WS-6's repository contract, or any other) is delivered, and an untouched 4.1.5 overlay ends
  byte-identical to a new 4.1.6 installation. `regenerate_adapters` re-projects `framework.json`; all indexes are rebuilt.
  The round-2 explicit `set_overlay_rule` for `spec/reports/memory-quality/**` is removed: the template is the single
  source (WS-6 IP-R2-2), and a migration adding a rule the template lacks would itself fail the convergence check.
- Notes: the convergence behaviour; the BC-P2-31 store locations; WS-10's IP-WS10-16 upgrade note (research/experiment
  schema 1.1.0, remediation, INV-013).

### Tests

- Lib `framework::tests::the_next_migration_converges_every_overlay_template_from_the_4_1_5_templates` (schema-valid;
  chain; a sync op per template with the exact 4.1.5 base; `check_substance` clean against the working templates; a
  4.1.5 overlay converges to the working templates, byte-identical where they differ; idempotent),
  `template_convergence_is_a_three_way_merge_that_keeps_customisations` (a synthetic IP-R2-11-shaped template:
  `spec/**` re-ordered, memory-quality rule inserted mid-list, blanket runtime rule replaced, `.governance-state/**` and
  `governance/registry/**` added, a field changed; an untouched overlay → exactly the template; a brownfield-style
  customised one keeps its prepended source rule, appended secret rule, deleted rule, customised field, and reports the
  one conflict; decisions on real paths), `the_substance_check_simulates_the_update_an_installed_project_receives`
  (a declared reconciliation that cannot add a rule and an appended rule are refused; sync accepted; wrong base refused),
  `template_convergence_dry_run_writes_nothing`.
- The round-2 unit test `the_next_migration_delivers_the_memory_quality_contract_rule` is replaced by the first test
  above (the migration no longer adds that rule on its own; see above).

### Coordination with WS-8 (version/payload decision) — IP-R3-WS09-2

`M-4.1.5-4.1.6` is complete for every overlay-template change and independent of which templates change. What it needs
from WS-8's decision is in IP-R3-WS09-2 (§9): if the working tree becomes 4.1.6, the consistency test and `release
build` check this record against `release/releases/4.1.5` and it converges by construction; if the tree stays 4.1.5
while `framework/overlay-templates` change, the same test checks the shipped `M-4.1.4-4.1.5` (byte-identical to the
immutable 4.1.5 release and not to be edited) and fails — the bump is the remedy, not an edit of the shipped record.

## 3. Command tests execute only what policy and the executing role permit (Contract v3 A3)

### Requirement

WS-9 r2 observation: a reviewer-authored `command` test runs an arbitrary command at A6/A7 with the executor's
privileges. Contract v3 A3: *"Tool execution respects role/authority/permission boundaries."* Bound what such a test
may execute to what policy and the declared roles permit, typed refusal otherwise, without defeating reviewer-authored
tests.

### What changed (`runtime/src/migrations/verify.rs`, `runtime/src/adopt.rs`)

- **What may run.** The command and its directory must be exactly one of the project's governed product-test commands —
  the ones the OS itself runs as product tests (`verification::product::plan`: `PROJECT_POLICY.tests` families or
  command, else the kernel's ecosystem convention; before the first install, the ecosystem convention) — or the A0
  behaviour baseline recorded in the T2-sealed adoption record (now with the directory it ran in; the scaffold's
  baseline test carries that `cwd`). Argument extensions are refused: a runner's own flags hand execution to another
  program (`go test -exec`, `make -f`, `cargo --config`, `git -c alias…`). A narrower command is declared as a test family
  in `PROJECT_POLICY` (a governed overlay change). The directory must be repository-relative without `..`.
- **Who may run it.** The executing role must hold `RUN_TESTS`: its `TOOL_PERMISSIONS.roles` entry when the policy lists
  the role (installed overlay, or the template the first install writes; an explicit entry decides, even an empty one);
  for a role the policy does not list, the duty the adoption protocol designates it — only A7's `migration-verifier`
  (protocol §3 Role D: "independently runs/extends tests"); nobody else. IP-R3-WS09-4 asks for the template to list the
  verifier explicitly.
- **How it runs.** Without the stage actor's declared identity (`GOV_ROLE`, `GOV_SESSION` removed), stdin closed.
- **Where it is enforced.** `TEST_COMMAND_NOT_PERMITTED` (test, command, stage, role, reasons, governed commands,
  permission basis, remediation) at A5 approval (against the A7 verifier, who executes every approved test), at A6
  before any batch (against the declared executor), at A7 before any test runs; inside the runner a refused command does
  not run and fails with its refusal; the legacy `run_tests_file*` entry points (no executing role) run no command test.
  Each executed command test records who was authorised and on what basis. The refusals are scoped to the stage that
  would bind or execute the command; re-review (A5) stays available.
- Reviewer-authored tests keep their purpose: every other kind is unchanged, and the governed behaviour baseline still
  runs at A6 (executor, TOOL_PERMISSIONS) and A7 (verifier, designated duty).

### Tests

- Lib `verify::tests::a_command_test_runs_only_a_governed_command_for_a_permitted_role`,
  `the_runner_executes_only_permitted_command_tests`; `adopt::tests::command_test_permissions_come_from_policy_and_the_designated_duty`.
- Certification `migration::command_tests_execute_only_governed_commands_for_permitted_roles` (migration fixture, pytest
  baseline): `sh -c touch PWNED`, `git -c alias.x=!…`, the governed command with extra arguments, and `cwd ../` are each
  refused at approval and nothing runs; the approved baseline command runs after batch 0 authorised by
  `TOOL_PERMISSIONS.roles.migration-executor`; with RUN_TESTS removed from the executor in the overlay, batch 1 is
  refused before anything moves; A7's report records the verifier's authorisation by designated duty.
- `probes/tiny_unprovisioned_adoption.py` CMD.1/CMD.2 on an unprovisioned bootstrap machine.

## 4. R3-9 — A11 states why, and names the posture when it is the only reason

- `a11_audit_by` records `verdict_reasons` for any verdict other than `ADOPTED_HEALTHY`: failed acceptance criteria,
  open high/critical adoption findings, a G5 verdict other than HEALTHY, the doctor verdict with the failing checks.
- When D032 is the doctor's **only** failing check, every criterion holds, no high adoption finding is open and the audit
  is HEALTHY (or finds nothing above `low` outside its own `installation_authenticity` disclosure), the reason is the
  posture: `verdict_reason {kind: installation_authenticity, check: D032, machine_posture, authenticity, admission,
  disclosure, remediation, message}`, first in the list, in the A11 result, the T2-sealed verdict (`reasons`, `reason`;
  adoption-baseline schema 1.2.0) and `12-ADOPTION-FINAL-REPORT.md` ("Why the verdict is …").
- Test: lib `adopt::tests::a11_names_the_installation_posture_when_it_is_the_only_reason`, fed the real D032 check of an
  unestablished installation (`srr::installation::doctor_check`): posture singled out alone; with the suite's own medium
  disclosure; not singled out when another check or criterion also fails.
- End-to-end on a real unprovisioned bootstrap adoption (`probes/tiny_unprovisioned_adoption.py`): the flow reaches A10
  and the doctor shows D032 with posture UNPROVISIONED / UNKNOWN / BOOTSTRAP_EMBEDDED_PAYLOAD, but A10 rejects on a
  builder starter query and D010/D021 also fail on that tiny project (observation O-1), so A11 is not reached there; the
  gated fixtures cannot run unprovisioned since P2-ADJ-0001 (no human channel without a provisioned root).

## 5. Regression and R1 preservation (at `16e4c0b`)

| Suite | Result | Baseline |
|---|---|---|
| `cargo test --lib` | **217 / 0** | 207 (+3 executor, +3 framework net, +2 adopt, +2 verify) |
| `cargo test --test certification` | **137 / 0** (six chunks: 12 + 4 + 10 + 33 + 52 + 26; `--list` = 137) | 136 (+1 `migration::command_tests_…`) |
| `cargo build --tests` warnings; rustfmt `--check` (edition 2021) on every touched Rust file | 0; clean | — |
| R1 held-out, unedited, private path `p2ar0040/r1-P2-AR-0040-private`, at `16e4c0b` (and at `adb9120`) | AR-0027 **26/3** (b1, b2, d3); AR-0029 **26/2** (b3, b6; `ho_f` does not compile); AR-0031 **27/7** (a1, a5, a8, b6, c2, c3, d2); AR-0033 **30/1** (`hv_a::a1` size pin) | identical to the recorded baselines |
| AR-0033 census (this tree) | **118 files / 2017 functions**; unpinned copy and `derive.py` (three splitter configurations): **0 violations** in every §6 activity | integration 118 / 1991 |
| Normalised R1 failure messages vs the round-2 integration run | **identical** (42 lines) | — |

The same certification suite also ran green at `adb9120` (137/0, `evidence/regression/cert-*.out`). No file under the R1
list (`srr/**`, `kernel_trust.rs`, `kernel.rs`, `lock.rs`, `init.rs`, `update.rs`, `release.rs`, `recovery.rs`,
`records.rs`, `tools.rs`, `capabilities/**`) changed; `recovery.rs` calls `executor::rollback_batch`, whose confinement
only narrows what a rollback writes. No new §6 effect; `section6::*` green. Contract v3 byte-identical.

## 6. Probes re-run

| Probe | Result on this tree | Note |
|---|---|---|
| round-2 WS-9/11 named checks (P2-AR-0032's labelled root-channel copy, unedited) | **41/41** | BC-P2-34/11/07/10 lines hold |
| synthesis AC16-X2 (unedited) | stops at `task claim TASK-W` (`TASK_NOT_RUNNABLE`, WS-5 BC-P2-16) before reaching `X2-B1B3` | premise changed by another merged repair; X2-B1B3 reads a newly initialised project's template, which is WS-6's (IP-R3-WS09-1) |
| `tiny_unprovisioned_adoption.py` (this run) | 5 PASS, 2 OBS | CMD.1/2, BOOT, SNAP, A7; observations A10 and DOC (O-1) |

## 7. Tests changed, and why

| Test | Change | Reason |
|---|---|---|
| `migration::path_migration_with_rollback_and_memory_rebuild` | tree hash excludes `.governance-state/**`; asserts the snapshot location, deletes `.governance-runtime/` before the rollback, asserts nothing refused | IP-R2-10: the snapshot is OS state in its store; the test now asserts more |
| `framework::tests::the_next_migration_delivers_the_memory_quality_contract_rule` | replaced by `the_next_migration_converges_every_overlay_template_from_the_4_1_5_templates` | the migration delivers the template (incl. that rule once WS-6's template carries it), no longer a rule of its own |

## 8. Other work in owned files

- WS-10 r2 IP-WS10-16 (release/migration authors, next migration): the upgrade note is in `M-4.1.5-4.1.6`.
- `migrations/README.md` states how template changes reach installed projects.
- Integration O-2 (WS-3's probe expects `session_source: "declared"`): unchanged on purpose; the adoption record states
  the declaration channel (`session: flag; role: flag`), a more precise statement of the same property.

## 9. Integration points (round-3 integration and later)

| IP | Owner / file | Exact change | Why |
|---|---|---|---|
| IP-R3-WS09-1 | WS-6, `framework/overlay-templates/REPOSITORY_CONTRACT.yaml` (+ `paths::to_framework_json`) | Put the IP-R2-11 / IP-R2-2 rules and order in the template itself. Nothing in `migrations/` needs to change: `M-4.1.5-4.1.6`'s `sync_overlay_template` delivers exactly what the template says, and `framework::tests::the_next_migration_converges_…` plus `check_substance` verify it after the merge. A `framework.json` projection change reaches installed projects through the migration's `regenerate_adapters` (and `update` regenerates adapters anyway). | template content is WS-6's; delivery is this migration's |
| IP-R3-WS09-2 | WS-8, `framework/KERNEL.yaml` (+ `runtime/src/lib.rs` VERSION constants, the release owner) | (a) If the working tree becomes 4.1.6: `version`/`cli_version`/`runtime_version` 4.1.6, `supported_from_versions` include 4.1.5 (and the chain), `schema_versions.migration: 1.2.0`, `adoption-baseline: 1.2.0`, `upstream-packet: 1.2.0`, `migration-catalogue-entry: 1.1.0`. `M-4.1.5-4.1.6` is then the migration into the current version and converges by construction. (b) Do not keep 4.1.5 while `framework/overlay-templates` change: the consistency test would check the shipped `M-4.1.4-4.1.5`, which must stay byte-identical to `release/releases/4.1.5`. (c) A lock or payload operation WS-8 needs (e.g. `set_lock_field`) is added to `M-4.1.5-4.1.6`'s `operations`, before `require_index_rebuild`; the `sync_overlay_template` operations and their bases stay as they are. | version/payload decision is WS-8's; the migration record is WS-9's |
| IP-R3-WS09-3 | WS-8, `tests/certification/common.rs` | `tree_hash`: add `.governance-state/**` to the default excludes beside `.governance-runtime/**` | every OS store moves there this round (WS-3/4/5/8/9); `migration.rs` passes it explicitly |
| IP-R3-WS09-4 | owner of `framework/overlay-templates/TOOL_PERMISSIONS.yaml` (WS-7 or the orchestrator's choice) | add `migration-verifier: [READ_REPO, RUN_TESTS]`, `migration-reviewer: [READ_REPO]`, `memory-verifier: [READ_REPO]` | the policy then states what the A7 designated duty grants today; `M-4.1.5-4.1.6` delivers the change to installed projects |
| IP-R3-WS09-5 | WS-1, `tests/governance/capability-evidence-map.yaml` | A3 (tool execution) → `migrations::verify::command_test_refusal`, `adopt` A5/A6/A7 pre-flight, `migration::command_tests_execute_only_governed_commands_for_permitted_roles`; B1/B3/D6 (adoption rollback material) → `executor::snapshot_dir`/`rollback_batch`, `migration::path_migration_with_rollback_and_memory_rebuild`; template delivery → `framework::check_substance`, `sync_overlay_template`, its lib tests; O5/BC-P2-36 disclosure at A11 → `adopt::verdict_reasons` | AC-10 evidence owners |
| IP-R3-WS09-6 | WS-3 (docs), `docs/COMMANDS.md` | document: `command` migration tests (governed commands only, RUN_TESTS, `TEST_COMMAND_NOT_PERMITTED`), A11 `verdict_reasons`/`verdict_reason`, the migration snapshot location, `sync_overlay_template` in `gov update` output | documentation |
| carried | round-2 IP-R2-1, -4, -5, -6, -7 (WS-3, WS-2, WS-3, WS-1, WS-3) | unchanged; IP-R2-2 → WS-6 (IP-R3-WS09-1), IP-R2-3 → WS-8 (IP-R3-WS09-2) | — |

No new subcommand, flag or `cli/src/main.rs` / `lib.rs` change.

## 10. Observations for routing (nothing changed for them)

| Id | Observation | Owner |
|---|---|---|
| O-1 | On a tiny unprovisioned bootstrap adoption (`probes/tiny_unprovisioned_adoption.adb9120.out`), A10 rejects on the builder's own starter query `HQ-008` (`exact_id` `MPLAN-GOVERNANCE-ADOPTION`, structured route): the plan record is indexed (`record_type migration-plan`) but not returned. Doctor there also fails D010 and D021 besides D032. | WS-6 (retrieval, structured route) |
| O-2 | `update.rs` runs `reconcile_overlay_defaults` for every template file, whatever the migration declares. After `sync_overlay_template` it is a no-op for converged files; it remains the path for historical chains. | WS-8 (no change needed) |
| O-3 | The template's rule order makes every `spec/**` path `authoritative` in current installations (WS-6 r2 O-1); the adoption evidence tree is indexed `authoritative` because of it (seen in O-1's index). | WS-6 (IP-R3-WS09-1) |

## 11. Limits and what this run did not do

- The template content (IP-R2-11/IP-R2-2) is WS-6's file this round; in this tree the templates equal 4.1.5's, so the
  migration's operations are no-ops here and the convergence is exercised by synthetic templates in the lib tests.
- The command bound is exact-command, not a sandbox: the OS cannot confine a spawned process (as TOOL_POLICY says for
  plugins). A governed test command runs the project's own test code, which is what `RUN_TESTS` means.
- The A7 verifier's permission comes from the protocol duty only while TOOL_PERMISSIONS does not list the role
  (IP-R3-WS09-4 makes it explicit). Agent identity stays adapter-declared (OWNER-DECISION-P2-0001).
- No end-to-end A11 on an unprovisioned machine (§4). No change to `cli/src/main.rs`, `lib.rs` or another workstream's
  file. No edit under `release/verification/`, `release/root-of-trust/`, `release/releases/`, `release/orchestration/phase-1/`,
  `release/capability-baseline/audit-0/` or another workstream's `repair-1/` directory.

**Owner-decision questions:** none. Every change stays inside ARCH-0001/ARCH-0003 and the active decisions; no trust
boundary, external dependency class or owner-controlled material is touched.

## 12. Evidence index (`evidence/`)

| Path | Content |
|---|---|
| `identity-and-scope.out` | product/governed digests (base, `adb9120`, `16e4c0b`), Contract v3 and frozen-gate-contract sha256, diffstat, ownership scope check (no path outside this run's files) |
| `regression/cargo-test-lib.adb9120.out`, `regression/cert-{A,B1,B2,C,D,E,F}.out` | lib 217/0 and certification 137/0 at `adb9120` |
| `regression/final-16e4c0b/` | lib 217/0 and certification 137/0 (six chunks, list count) at `16e4c0b` |
| `r1-heldout/run-r1-heldout.sh` | P2-AR-0032's runner with only the run id, scratch root, jobs count and a suite selector (tool time limit) changed; the labelled `hv_a` copy it uses |
| `r1-heldout/r1-heldout-{adb9120,16e4c0b}-*.out` | the four suites, census, S1, S2 at both commits |
| `r1-heldout/failure-messages-{vs-integration,final-vs-integration}.txt` | normalised failure messages identical to the round-2 integration run |
| `probes/R2-ws0911-named-checks.root-channel.adb9120.out` | 41/41 |
| `probes/AC16-X2-authority-gate-chain.adb9120.out` | unedited synthesis probe (stops before X2-B1B3, §6) |
| `probes/tiny_unprovisioned_adoption.{py,adb9120.out}` | this run's probe (§3, §4, O-1) |

Outputs contain this run's absolute scratch paths (`…/scratchpad/p2ar0040/…`).

## 13. Process disclosures

- Model Claude Opus 5 (1M context), `claude-opus-5[1m]`. No sub-agent, no contact with the product owner, no session or
  agent transcript, task-output store or user auto-memory read. Every long command ran in the foreground with its output
  redirected into this evidence directory.
- The permission system denied one compound shell command (it began with `rm -rf` of a scratch directory). It was not
  retried as written; the scratch scenario was recreated under a fresh directory with plain `mkdir` and file writes.
- My own drafts had defects fixed before the recorded runs: the convergence test first expected an appended project rule
  to stay after new template rules (the design anchors it last, so the test was wrong and was corrected after the design
  was settled); the executor refusal count; the command-test certification scenario read a ledger batch 0 never writes;
  the first tiny-project verifier queries picked empty `.gitkeep` files.
- The R1 held-out runner was given a `SUITES` selector because a single invocation exceeds the tool's time limit; every
  suite ran, unedited, across two or three invocations per commit (all four suites and both supplementaries at each).
