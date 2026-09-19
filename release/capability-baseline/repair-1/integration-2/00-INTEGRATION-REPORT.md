# P2-AR-0032 — Repair iteration 1, round 2: integration report

| Field | Value |
|---|---|
| Run | P2-AR-0032, fresh `capability-repair` **integration builder**, model Claude Opus 5 (1M context), `claude-opus-5[1m]` |
| Handoffs | P2-HO-0030 (round-2 integration); P2-HO-0019 (integration method); P2-HO-0020 and P2-HO-0010 (protocols); each round-2 builder's `repair-1/r2-<ws>/00-REPAIR-REPORT.md` |
| Branch / base | `phase2/repair-1-r2-integration` from `a7e94733add3fbe355802b971d5e94f5997dfbab` |
| Merged | `phase2/repair-1-r2-ws03` `7a5d397`, `-ws08` `9a38329`, `-ws05` `1fa60c6`, `-ws04` `9e80678`, `-ws02` `9e8f06f`, `-ws06` `33627c8`, `-ws07` `bca26c4`, `-ws09-11` `4e1aade`, `-ws10` `c0d45c1` (all from `843d79c`), in that order, `--no-ff` |
| Integrated product tip | **`7491c5ca78ee2a7772571892cede623416e84324`**. `product_code_digest 797da37c8532528e1b8f3d924e2b7b7a304bb567bd928ce80126e8e120161fe1`. `governed_state_digest 8f191e3906850368eb82bc886d5a095a788469103ed7318a9236462464ae948f` (this changed from the base's `4981437f…227d` through WS-3's `docs/` update, not through an integration change). The commit that adds this report and `evidence/` changes no product file, so it carries the same `product_code_digest`. |
| Verdict | **`READY_FOR_INDEPENDENT_CAPABILITY_VERIFICATION`**. The integrated tree builds with no warnings, and every suite is green: `cargo test --lib` 207/0, `cargo test --test certification` 136/0, Python plugin tests 4/4, rustfmt clean on every touched file. Every prior R1 held-out suite is at its recorded baseline. The one exception is the known AR-0033 `hv_a::a1` size pin (census 118 files / 1991 functions, 0 violations in every §6 activity). One builder-probe line cannot be brought back without a semantic decision in WS-2's file (IF-1, §7.2). It is routed, not repaired, and it is not a suite failure. Nothing was stopped as a contradiction. |

This is an integration builder's record. It grades no repair and claims no class, and every result below is regression
evidence (Contract v3 O3). Acceptance belongs to the fresh independent verifiers.

---

## 1. Merges

All nine branches were merged with `git merge --no-ff` in the handoff order. Each conflict was resolved as the union of
both sides' intent, and no other edit went into a merge commit. `evidence/merge-and-change-log.out` holds the parents and
the `git show --cc` of each merge. `identity-and-scope.out` shows that the merges brought in only files the nine branches
changed.

| Merge | Conflict | Resolution |
|---|---|---|
| `41e79a7` ws03 | none | — |
| `0660970` ws08 | `tests/certification/update.rs`, `repair.rs` (`update_approval_requires_presented_answered_gate`), `repair2.rs` (4.1.2→current chain). WS-3 and WS-8 had each provisioned these machines, with identical key material. | WS-8's harness side (the convergence target, §3). WS-3's stronger assertions are kept: the exact `release:…@<VERSION>` lock source for the current release (WS-8 had only `starts_with`) and the `{lock}` diagnostics. |
| `0cca917` ws05 | `repair.rs` (scope test set-up); `repair2.rs` and `ws03.rs`, where WS-3 and WS-5 had both moved the D027 doctor/audit block after the packet compile | Union: WS-8's signed `init` plus WS-5's `traceable_inputs`. One D027 block is kept (WS-5's, which asserts a superset: the hard-block envelope also names D027). The duplicated copy is removed. |
| `be3ca2b` ws04 | `tests/certification/main.rs` | both `mod` lines |
| `79b0098` ws02 | none | — |
| `92bd0bd` ws06 | `cli/src/main.rs` `g0_label` (`MemoryCmd::Miss/Failures`, WS-3 vs `Integrity/Profile`, WS-6); `main.rs` | all four arms; both `mod` lines |
| `d1dc020` ws07 | `main.rs` | both `mod` lines |
| `3fad1c9` ws09-11 | `migration.rs`: WS-2's appended helper vs WS-9's appended test | both |
| `0f830f3` ws10 | `cli/src/main.rs`: `Cmd::Session` (WS-4) vs `Research/Experiment/Data/Scenario` (WS-10) variants, their `g0_label` and `command_name` arms | all variants and arms |

Several overlapping edits merged without textual conflict and were reviewed by hand: `greenfield.rs` (WS-8's signed
`init`, WS-3's channel call, WS-5's designated roles and receipts), `ws03.rs` (WS-3's helpers and new tests with WS-8's
`fresh`/`fresh_unprovisioned`), and `control.rs` (additive `COMMAND_GUARDS` from five workstreams).

Straight after the merges and the compile reconciliation (`547d65d`): lib 207/0, certification **109/27**
(`evidence/regression/*.after-merges-547d65d.*`).

## 2. Every change beyond the merges

Four commits, 12 files, +228/−166 (`evidence/regression/rustfmt-warnings-diffstat.out`). Two files are product code; neither
is on the R1 list (`srr/**`, `kernel*.rs`, `lock.rs`, `init.rs`, `update.rs`, `release.rs`, `recovery.rs`, `records.rs`,
`tools.rs`, `capabilities/**`). The other ten are certification tests. No schema, check, policy or kernel-payload file
changed. No default role, unauthenticated answer path or standalone human-gate anchor was introduced.

| Commit | Files | Kind | Change and reason |
|---|---|---|---|
| `547d65d` | `runtime/src/memory/profile.rs` | compile reconciliation (WS-6 × WS-7) | WS-7 removed `capabilities::governance::command_files`, its trust-on-first-use pin helper, and WS-6's retrieval-profile adapter identity imports it. The union did not build. The listing WS-6 was built and tested against is now a private helper in `profile.rs` with identical behaviour. WS-7's execution binding (`capabilities::binding::resolve`) is untouched and still decides which bytes a plugin may run. |
| `bcf0139` | `runtime/src/cit/propagation.rs` | semantic reconciliation (WS-4 × WS-5) | §4.1 |
| `9c4af7e` | `tests/certification/{ws03,ws04r2,ws05,ws06,ws07,ws08_r2,repair}.rs` | harness convergence; builder-test updates | §3, §4.2–§4.5 |
| `7491c5c` | `tests/certification/{brownfield,migration,repair2}.rs` | WS-2's temporary D032 relaxations removed | §5 |

## 3. One harness convention (handoff: test-setup overlap)

The suite now uses WS-8's provisioned root everywhere, with `human-gate` delegated to the test owner (WS-3 IP-R2-4;
WS-8 IP-R2-WS08-12):
- `common::setup_fixture` provisions the scenario machine with the suite's throw-away root.
- Every install is `--source common::signed_source()`, or `signed_copy` for historical releases.
- Below-floor rollbacks carry `common::break_glass`.
- `ws03::human_channel` finds the channel already available and uses it as is.

What changed, and why no asserted property was lost:
- **The overlapping files** (`update.rs`, `repair.rs`, `repair2.rs`) take WS-8's side, with WS-3's stronger assertions
  added (§1). Both sides asserted the same properties: provision, then install signed releases; the refused, then
  break-glass rollback; the lock basis `release:`.
- **`ws03.rs` helpers.** `throwaway_root`, `provision`, `signed_release`, `break_glass_for` and the re-anchor publisher
  now delegate to `common::{suite_root_file, provision, sign_release, break_glass}`. That gives one root (the same key
  material and delegation) for the whole suite, and `ws03::provision` becomes idempotent. Without this,
  `ws03::a_project_on_a_shipped_older_kernel…` provisioned twice (`SRR_ALREADY_PROVISIONED`).
- **The P2-ADJ-0001 test** (`the_standalone_human_gate_anchor_is_off_…`) is about an unprovisioned machine, so it now
  uses WS-8's `fresh_unprovisioned`, as WS-8 had already done for `human_answers_come_only_from_the_owner_signed_channel`.
  Every assertion is unchanged.
- **The new round-2 builder tests** (`ws04r2` 5, `ws05` 7, `ws06` 4, `ws07` 5) installed the embedded payload. On a
  provisioned machine that is refused `SRR_RELEASE_UNVERIFIED`, which is R1 behaviour. They now install
  `--source signed_source()`, as WS-8 changed every earlier test.
- **`ws08_r2::newer_external`.** The hypothetical 9.9.9 release copies the canonical `migrations/`, which now also holds
  WS-9's prepared `M-4.1.5-4.1.6`. The chain resolver follows the first step from the installed version, so
  `update --apply` stopped at `UPDATE_UNSUPPORTED` before the admission refusal the test asserts. The fixture now keeps
  only its own step from the current version. `update::check`/`apply` are unchanged.

## 4. Semantic reconciliations

### 4.1 WS-4 × WS-5: propagation re-seals the OS-sealed records it marks (`bcf0139`)

- **Failure.** `greenfield_end_to_end` failed: the implementation close was refused `INDEPENDENCE_VIOLATION` on
  `TST-0001`, "no sealed close report produced its current content".
- **Cause.** WS-5 T2-seals close reports and establishes recorded authorship (BC-P2-34), and close attribution, only from
  reports whose seal verifies. WS-4's CIT-E propagation (BC-P2-04) writes a `staleness` block into the closing reports of
  dependent work. That broke `RPT-0003`'s seal, and `RPT-0003` is the independent test designer's report and the recorded
  authorship of `TST-0001`. WS-2's `os_binding_integrity` would also report the broken seal as tampering.
- **Change.** `cit::propagation::save_set` is the single writer of propagation markers. It now re-seals a record after
  marking it, with operation `cit propagation`, but only when the record's seal verified before the write. A record whose
  seal does not verify (unsealed, edited, foreign) is marked and never sealed: the OS does not bless content it did not
  write. WS-10's `lifecycle::record_influence` already follows the same rule.
- **Scope.** This is the first option WS-5 stated for its IP-R3-3, applied only because the union failed without it. The
  rest of IP-R3-1/2/3 stays with round 3 (§8, O-7). A hand edit of a report still breaks its seal.

### 4.2 WS-3 × WS-9: adoption producer provenance (test assertion)

WS-3's CLI hands `adopt map|plan` the declared session (`Actor::declared`). WS-9's round-2 `identity::resolve_actor`
re-verifies it against the process declaration and records the channel: `session_source: "session: flag; role: flag"`
instead of the literal `"declared"`. The property WS-3's test asserts still holds: the declared session and role are
recorded, never the A0 fallback. `ws03::round_two_call_sites…` now asserts WS-9's exact string. No product change was made.

### 4.3 Other workstreams' rules in the new builder tests

These tests were each written on a branch without the other repair. They are updated to take the legitimate path, and no
assertion was removed:
- **`ws06` (WS-7 BC-P2-39).** The local embedder and the rerank plugin are registered through `ws07::register_approved`
  (owner-answered gate). The revision-2 descriptor is first shown not to execute unregistered, then registered, so the
  test still measures WS-6's own revision-pin refusal (`EMBEDDER_REVISION_MISMATCH`).
- **`ws06` (WS-5 BC-P2-16).** The claimed implementation task declares its scenario and acceptance test
  (`ws05::traceable_inputs`).
- **`ws04r2::upstream_change_reaches_completed_work` (WS-5 BC-P2-20, WS-2 BC-P2-43).** The close report is a consumption
  receipt (`ws05::receipt`). Because the scenario runs no product tests, it states `not_applicable_with_reason`, WS-5's
  convention.
- **`ws08_r2` adopt ingress (WS-9 BC-P2-34).** The designated reviewer authors tests before approving
  (`migration::reviewer_authors_tests`).

### 4.4 WS-2 × WS-4 × WS-5: W7 remediation in `repair::task_close_enforces_mutation_scope`

The test's governed CIT executed while the worker's out-of-scope `SCN-0099` was still on disk:
1. WS-4's G4 tier after CIT-E (IP-WS02-06) ran WS-2's W7 remediation (BC-P2-22), which generated an investigation task
   with an `AFFECTS` edge to `SCN-0099`.
2. Removing `SCN-0099`, the remedy the test asserts, left that edge dangling. `graph_integrity` then reported a medium
   finding, the suite was DEGRADED, and WS-5's close gate refused the governance-affecting close
   (`GOVERNANCE_SUITE_STALE`). Cancelling the investigation task does not clear the edge (measured on a copy); only a CIT
   editing the generated task would.

Each repair behaves as specified. The test now executes the CIT straight after the claim, before the out-of-scope write,
and every assertion is unchanged. The interaction is routed as O-1 (§8).

## 5. WS-2's temporary D032 relaxations removed (`7491c5c`)

WS-2 (R3-7) accepted D032 as the sole failure on an unprovisioned machine in three places:
`brownfield_adoption_end_to_end`, `path_migration_with_rollback_and_memory_rebuild` (the `adopted_but_for_unprovisioned_posture`
helper, one copy each), and the 4.1.2→current chain (a D032 doctor filter). With WS-8's harness merged, those machines are
provisioned. The relaxations are gone, the strict assertions apply (`ADOPTED_HEALTHY | ADOPTED_WITH_ACCEPTED_EXCEPTIONS`;
only D021 may fail after the chain), and all three tests pass. The scenarios that are deliberately unprovisioned are
different tests: `repair::embedded_kernel_installs_without_canonical_root`, `repair2` lock identity, `ws03` HC/ADJ, and
`ws08_r2`. Each asserts the refusal or the BOOTSTRAP marking; none tolerates it.

## 6. Standalone anchor, guard registration and the secret-like literal

- **Standalone anchor (P2-ADJ-0001).** No test re-enables it. The remaining references assert its refusal
  (`ws03` HC/ADJ). Builder probes written against the old default use the provisioned root through labelled derived
  copies (§7); the anchor itself stays off.
- **G0 registration** (`evidence/g0/round2_labels_g0_probe.{py,out}`, **11/11**; certification
  `ws03::every_cli_command_label_is_classified_by_g0` passes). Every round-2 label is classified once, among 177 labels
  with no duplicates. Each authority class it names is declared in `AUTHORITY_POLICY`:

  | Labels | Class |
  |---|---|
  | `health qualify` (WS-2) | Write / `record_audit` (L0, treated exactly as `audit`) |
  | `memory miss` / `memory failures` (WS-3) | Write / `record_failure_memory` (L1); Read |
  | `cit classify`, `cit propagate --dry-run`, `context staleness`, `checkpoint freshness` (WS-4) | Read |
  | `cit propagate` / `session close` (WS-4) | Write / `simulate_cit`; Write / `checkpoint` |
  | `memory integrity`, `memory profile` (WS-6) | Read |
  | `memory select --gate` (WS-6) | keeps `memory select`: Write / `memory_select` |
  | `research record\|update\|conclude\|withdraw\|sync`, `experiment design\|update\|run\|reproduce\|conclude\|abandon`, `data register` (WS-10) | Write / `mutate_spec_other` |
  | `experiment promote` (WS-10) | Write / `approve_cit_human` |
  | `research\|experiment show\|check`, `data show`, `scenario trace\|check` (WS-10) | Read |

  WS-7 and WS-9/11 added no subcommand. The probe checks each label's true class on a populated project:
  - Every Read label runs and changes no governed file, unfrozen as well. The undetected direct upstream edit stays
    unpropagated after `cit propagate --dry-run`.
  - Under FREEZE_WRITES and PAUSE, every Write label is refused FROZEN/PAUSED (exit 4) and writes nothing.
  - An undeclared invocation is refused `AUTHORITY_DENIED` for every L1+ Write label.
  - Unfrozen, the Write labels do write: propagation markers, the session-close checkpoint, a memory-quality record.

  No registration change was needed.
- **Secret-like literal** (`evidence/secret-literal/check-secret-literal.{sh,out}`). `framework/KERNEL.yaml`
  `payload_dirs` has no `health`, and `kernel::stage_payload` copies only payload dirs. Across the 718 certification
  scratch trees of this run, no installed kernel carries `health/`. The copies of the file are release-source and
  canonical-tree fixtures (`ws08_r2`, `srr` contract tests) and machine-local embedded-kernel caches; none is a scanned
  project. One test puts that cache inside its project tree; it runs no scan (O-5). The literal's semantics were not
  changed (WS-2 round 3).

## 7. Regression

### 7.1 Suites at `7491c5c` (`evidence/regression/`)

| Suite | Result | Expected |
|---|---|---|
| `cargo test --lib` | **207 / 0** | 146 + WS-3 3 + WS-8 1 + WS-5 5 + WS-4 14 + WS-2 5 + WS-6 3 + WS-7 9 + WS-9/11 7 + WS-10 14 = 207 |
| `cargo test --test certification` | **136 / 0** (two parts, 58 + 78; `--list` = 136; includes `section6::*` 9, `srr::*` 21, `ws03::*` 15, `ws08_r2::*` 10) | 100 + WS-3 3 + WS-8 10 + WS-5 7 + WS-4 5 + WS-6 4 + WS-7 5 + WS-9/11 2 = 136. After the merges: 109/27 |
| Python plugin tests | **4 / 4** | 4 |
| rustfmt `--check` (edition 2021), every file changed after the last merge | 0 hunks each (all were clean as merged) | — |
| `cargo build`, `cargo test --no-run` warnings | 0, 0 | — |

`CARGO_BUILD_JOBS=6` throughout.

### 7.2 R1 held-out suites, unedited, private path (`evidence/r1-heldout/`)

The suites ran through `run-r1-heldout.sh`, which is WS-8's runner with only the run id, the scratch root and the jobs
count changed. Each copied file is `cmp`-identical (28 `identical` lines). The private scratch root is
`…/scratchpad/p2ar0032/r1-P2-AR-0032-private`, whose `wt/srr1-r1-verify{,-2,-3,-4}` links point at this worktree only.
The run is at HEAD `7491c5c` with 0 product files differing.

| Suite | Recorded baseline | This tree |
|---|---|---|
| AR-0027 | 26 / 3 (`b1`, `b2`, `d3`) | **26 / 3**, same tests |
| AR-0029 | 26 / 2 (`b3`, `b6`); `ho_f` does not compile | **26 / 2**, same tests; `ho_f` does not compile |
| AR-0031 | 27 / 7 (`a1`, `a5`, `a8`, `b6`, `c2`, `c3`, `d2`) | **27 / 7**, same tests |
| AR-0033 | 31 / 0 (30 / 1 on any larger tree) | **30 / 1**: `hv_a_derivation::a1` only (pins 84 / 740) |

- **Census** (AR-0033's walk of this tree): **118 files / 1991 functions**. That is 105 + WS-2 2 + WS-4 4 + WS-6 2 +
  WS-7 1 + WS-10 4 new source files.
- **Unpinned copy.** The labelled copy `hv_a_derivation.a1-unpinned.P2-AR-0032.rs.txt` changes only the two size
  assertions (the diff is in the output). It finds **0 violations in every §6 activity**:

  | Activity | Derived | Writers | Exempt |
  |---|---|---|---|
  | human_gate_create | 47 | 42 | 1 |
  | human_gate_approve | 1 | 1 | — |
  | release_certification | 1 | 1 | — |
  | trust_policy_mutation | 8 | 1 | — |
  | privileged_plugin_acquisition | 9 | 2 | — |
  | floor_lower_or_reset | 3 | 1 | — |
  | present_below_floor_release_as_current | 1 | 1 | — |
- **Independent derivation.** AR-0033's own `derive.py` (ROOT line only) agrees under all three splitter configurations,
  with 0 violations.
- **Failure messages.** The normalised failure messages of the unedited suites are identical, 42 lines each, to the
  round-1 integration's final run and to WS-8's round-2 run (`failure-messages-vs-prior-runs.txt`).
- **Structural invariants.** WS-8's R1 invariants script re-run on this tree finds them all as WS-8 recorded
  (`builder-probes/unedited/ws08-r1-invariants.out`):
  - one verifier at 5 ingress sites;
  - the floor check, break-glass and `PERMITTED_OPERATIONS` byte-identical to base;
  - no floors writer outside `state.rs`;
  - `kernel_trust.rs` free of SRR verdict vocabulary;
  - no signing capability;
  - the owner-closed functions identical.

### 7.3 Round-2 builders' own probes against the integrated binary (`evidence/builder-probes/`)

`run-builder-probe.sh` runs each builder's probe **unedited** (`unedited/`). Where a line failed only on a path another
merged repair removed by design, it runs a **labelled derived copy** (`derived/`, runs in `derived-runs/`). Every derived
file's header lists each change. `compare_builder_probes.py` pairs every verdict line with the builder's recorded
after-run (`COMPARE-builder-probes.out`).

| Builder probe | Builder's branch | Integrated, unedited | Integrated, derived | Why the unedited run differs |
|---|---|---|---|---|
| WS-2 `WS02-r2-supplementary` | 51/51 | 48/51 | **50/51** (fixtures) | W7.5b/W7.2b: the fixture's question+conclusion-only research is HIGH `schema_invariants` under WS-10 (BC-P2-47), and WS-2's hard-block then refuses the close through WS-5's gate. SUITE.delivery: WS-5 stores a READY task with a missing input as BLOCKED, so nothing is dispatchable. Derived: J1-complete research, a task whose input disappears after it is READY, and a WS-5 receipt at close. **W7.2b still fails: IF-1.** |
| WS-3 `R2-WS03-probes` | 24/24 | 23/24 | — | `CS.a`: WS-9's refined provenance string (§4.2); the property holds |
| WS-3 `ws03_named_checks.r2-derived` | 39/39 | **39/39** | — | — |
| WS-4 `ws04r2-scenarios` (through the evidence adapter) | 40/40 | stops at S1's first answer | **40/40** | The round-1 adapter provisions a standalone anchor. Derived adapter (WS-5's adapter, which also completes receipts, plus the root channel) with the unedited scenario: 39/40. `S4.boundaries-observed` fails because WS-5 already derived `t2` BLOCKED, so `task status t2 BLOCKED` is no transition. Derived scenario (the hold set on `t1`): 40/40. |
| WS-5 `ws05_r2_supplementary` | 37/37 | 31/32 (section B not run) | **37/37** | standalone anchor |
| WS-6 `SUPP-ws06-r2` | 8/8 | stops at R3 | **8/8** | standalone anchor; R5's claimed task is an implementation task WS-5 makes non-runnable (a documentation task in the copy) |
| WS-6 `SUPP-ws06-behaviours` (round 1, re-run by WS-6) | 19/19 | 16/19 | **19/19** | S1/S4: a hand-declared executable `code_intel` plugin never runs under WS-7 (BC-P2-39), and the indexer falls back silently (WS-7 IP-W7-2). The copy registers it through the owner's gate. |
| WS-7 `ws07_named_checks` | 26/26 | 5/9 (4 scenarios stop) | **26/26** | standalone anchor |
| WS-8 `WS08-P1..P4`, R1 invariants, `cold_cache_scheduler` | P1 14/15, P2 8/8, P3 11/11, P4 9/9 then the K5 stop; all invariants; 17/17 | **identical** | — | — (P1 `R2a` fails by WS-8's design, as WS-8 recorded) |
| WS-9/11 `R2-ws0911-named-checks` | 41/41 | 38/41 | **41/41** | standalone anchor (`gate-subject`, `Q-declined`, `Q-human`) |
| WS-10 `ws10_supplementary` | 35/35 | 10/12, then stops | **35/35** | Standalone anchor. WS10-J1-8 calls `memory select`, which under WS-6 (BC-P2-30) now raises the R5 gate first; the copy answers it and re-runs with `--gate`. |

The derived channel is `derived/p2ar0032_root_channel.py`. It does what WS-3's own derived named checks do:
- provision the throw-away root of `r2-ws03/evidence/hc_root.py`, whose `human-gate` key is `hc_owner.py`'s seed 7;
- re-verify the installed kernel against a signed release of the pinned payload.

It never re-enables the standalone anchor.

**Integration regressions.** Apart from IF-1, every line that passed on a builder's branch also passes integrated
(directly, or through a copy that changes only a path WS-3 removed by design or a fixture premise another merged repair
changed). The differences are those listed in the table.

**IF-1 (not repaired; routed to WS-2): W7 delivery-gap detection × WS-5 receipts.**
- **What happens.** WS-2's line W7.2b asserts that once implementation work of a feature is DONE, an untouched
  requirement of that feature is a W7 delivery gap (medium). On WS-2's branch the close used a bare report. Under WS-5
  (BC-P2-20) a close must be a receipt, and the receipt must acknowledge every mandatory input, including the feature's
  inherited requirements (`inputs_consumed`), and state what it did not implement (`deviations`).
- **Mechanism.** `inputs_consumed` is a `CONSUMES` relation field (round-1 WS-4, `records.rs`). WS-2's
  `lineage::specs_without_path` counts any work node that reaches a requirement through an `IMPACT_IN` in-edge,
  `CONSUMES` included, as an implementation path.
- **Consequence.** A requirement that the closing receipt explicitly declares *not implemented* (for example
  `"REQ-0002: not implemented by this task"`) is no longer reported, and in the union W7.2b can no longer fire through the
  product's close path. Evidence: `derived-runs/derived_WS02-r2-supplementary.fixtures.P2-AR-0032.py.out` and the
  closing report quoted in §8.
- **Why it is not repaired here.** Fixing it means deciding what counts as a W7 "downstream implementation path"
  (Contract v3:1140). One option counts a report only through `IMPLEMENTS`/`VALIDATED_BY`; another excludes inputs a
  receipt names as deviations. That is WS-2's BC-P2-22 semantics and changes which orphans, and so which remediation
  tasks, the suite produces. It is not a minimal integration change, and the two repairs' requirements do not contradict.

## 8. Observations for routing (nothing changed for them)

| Id | What | Owner |
|---|---|---|
| IF-1 | §7.3. Closing receipt of the reproduction: `requirements_implemented: [REQ-0001]`, `inputs_consumed` includes `REQ-0002`, `deviations: ["REQ-0002: not implemented by this task (left for later work of the feature)"]`; the G5 audit lists no orphan for `REQ-0002`. | WS-2 (BC-P2-22), round 3 |
| O-1 | §4.4. A record that became the subject of W7 remediation (generated at any persisted G4-G6 run, including the G4 after CIT-E) and is then deleted leaves a dangling `AFFECTS` edge. The suite is DEGRADED and governance-affecting closes are refused until a CIT repairs the generated task; cancelling it is not enough. This compounds WS-5's O-R2-1 (a DEGRADED suite refuses governance-affecting closes). | WS-2 (with WS-5 O-R2-1) |
| O-2 | WS-3's probe `CS.a` expects `session_source: "declared"`; WS-9 records the declaration channel. | WS-3/WS-9 (wording) |
| O-3 | A hand-written research note presented as evidence without its J1 fields is a HIGH `schema_invariants` finding. Through WS-2's hard-block and WS-5's close gate it refuses task close (WS-10 §6.1 predicted this; seen in WS-2's probe fixture). | WS-10 / WS-2 (policy choice already stated by WS-10) |
| O-4 | WS-5's derived status changes other builders' fixture premises. `task create --status READY` with a missing input stores BLOCKED. `task status X BLOCKED` on an already derived-BLOCKED task is not a transition, so WS-4's boundary observer sees none. | verifiers / probe authors |
| O-5 | `repair::embedded_kernel_installs_without_canonical_root` sets `GOV_KERNEL_CACHE` inside its project. The embedded-kernel cache (every embedded file, WS-2's `health/` included) lands in the project tree. A scan of that project, measured on a copy, reports D011 critical (the planted `AKIA…EXAMPLE`) and D013; the test itself runs no scan. | test owner; the literal is WS-2's (IP-R2-WS08-6) |
| O-6 | WS-7's IP-W7-2 is confirmed on the union: a refused `code_intel` plugin is skipped silently by the indexer (WS-6 round-1 S1/S4 unedited). | WS-6 (IP-W7-2) |
| O-7 | `bcf0139` covers propagation's writer only. The other OS writers that modify sealed records remain round-3 items: WS-2 R3-1 (CIT rollback marks a sealed decision REJECTED without re-sealing), WS-5 IP-R3-1/-2/-3 (task and CIT sealing, other marker writers). | WS-4 / WS-3 / WS-5, round 3 |
| O-8 | `greenfield.rs` keeps WS-3's `crate::ws03::human_channel(&g)` after `init`. On the harness-provisioned machine it finds the channel available and does nothing. | — |
| O-9 | Every builder's open round-3 integration points stand as each report lists them (WS-2 R3-1..12, WS-3 IP-R2-1..6, WS-4 R2-1..15, WS-5 IP-R3-1..10, WS-6 IP-R2-1..13, WS-7 IP-W7-1..8, WS-8 IP-R2-WS08-1..13, WS-9/11 IP-R2-1..7, WS-10 IP-WS10-01..17). None was wired beyond what the union needed to build and pass. | round 3 |

## 9. Contradictions and stopped items

None stopped. No two repairs require contradictory behaviour. Each conflict found has a resolution that keeps both sides'
requirements: §4.1 through §4.4 and §3. IF-1 is routed rather than repaired because it needs a semantic decision in one
workstream's file (§7.3). It is not a contradiction between the two repairs' requirements.

## 10. What I did not do

- I started no round-3 class. The only integration point touched is IP-R3-3's report part (§4.1), because the union's
  certification suite failed without it.
- I changed no probe, held-out suite, audit-of-record file, schema, policy or kernel payload. Derived copies and adapters
  live only under `evidence/builder-probes/derived/` and are labelled.
- I did not change the secret-like literal (WS-2 round 3), register `framework/health` in `payload_dirs`, or re-enable
  the standalone anchor anywhere.
- I did not rebase, tag or push, and I touched no other branch or worktree. Other branches were read with `git show` /
  `git diff` only.

## 11. Evidence index (`evidence/`)

| Path | Content |
|---|---|
| `merge-and-change-log.out` | merges and parents, `git show --cc` of each merge, every integration commit's stat |
| `identity-and-scope.out` | product/governed digests (base, merges-only `0f830f3`, final `7491c5c`, each builder tip); Contract v3 sha256; release binary sha256; protected-path and merge-scope checks |
| `regression/` | final lib (207/0) and certification (58 + 78 = 136/0; list count); after-merges runs (lib 207/0, certification 109/27); Python 4/4; rustfmt, warnings, diffstat |
| `r1-heldout/` | runner, labelled `hv_a` copy, run output at `7491c5c` (census, S1, S2), normalised failure-message comparison |
| `g0/` | round-2 label probe (11/11) |
| `secret-literal/` | the kernel-payload and scan-scope check |
| `builder-probes/` | runner; `unedited/`, `derived/` (each copy's header lists its changes), `derived-runs/`, `derived-runs-r1-adapter/` (the round-1-adapter derivation, superseded because the scenario's closes need WS-5's receipt completion: S1-S2 14/14, then `RECEIPT_INVALID`); `compare_builder_probes.py`; `COMPARE-builder-probes.out` |

Outputs contain the absolute scratch paths of this run. Scripts take `P2AR0032_SCRATCH` and write only under this
directory or the scratch directory.

## 12. Process disclosures

- Model Claude Opus 5 (1M context), `claude-opus-5[1m]`. I spawned no sub-agents, did not contact the product owner, and
  read no session or agent transcripts, task-output stores or user auto-memory. Every long command ran in the foreground.
- The permission system denied one shell command: it replaced an earlier scratch copy with `rm -rf` and copied machine
  state into the certification harness's `/tmp/gov-cert-machine`. I did not retry it as written. I redid the step by
  copying into a fresh scratchpad directory with an explicit machine-state home (`govx.sh` in scratch).
- My own probe drafts had defects, each fixed before the recorded run:
  - The G0 probe put experiment outputs in the production tree (refused, correctly) and read record ids from the wrong
    result keys.
  - The WS-10 derived copy first read the select gate as `gate` instead of `human_gate`.
  - The WS-2 derived copy needed three iterations (J1 fields, then receipt fields, then the deviation for REQ-0002). The
    recorded run is the final copy; runs under the same label were overwritten.
- The certification harness writes its scenario trees under `/tmp` (`gov-cert-*`, `gov-cert-machine`). That is its
  existing behaviour. To force a rebuild for the warnings count, I `touch`ed two source files (their mtime only).
