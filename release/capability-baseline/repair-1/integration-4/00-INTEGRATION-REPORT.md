# P2-AR-0054 — Repair iteration 1, round 4: integration report (the tree that becomes `cap2-candidate-1`)

| Field | Value |
|---|---|
| Run | P2-AR-0054, a fresh `capability-repair` **integration builder**. Model: Claude Opus 5 (1M context), `claude-opus-5[1m]` |
| Handoffs | P2-HO-0049 (round-4 integration). Method from P2-HO-0040, P2-HO-0030 and P2-HO-0019. Rules from P2-HO-0031 (availability rule), P2-HO-0020 (incl. the R1 private-path census rule) and P2-HO-0010. Owner decision **OD-P2-03** (`GATES/OWNER-DECISION-P2-0003-TOOL-INSTALL-GATE.md`), in force. Both round-4 records: `r4-ws01/00-REPAIR-REPORT.md`; `r4-residual/00-REPAIR-REPORT.md`, `01-CONTINUATION-REPORT.md`, `02-OD-P2-03-REPORT.md`, `claims.yaml` |
| Branch / base | `phase2/repair-1-r4-integration`, from `c0af4e6491d354b35ff91d6b56ac0020fec061c8`. Its product tree is the round-3 integrated tree (merge `e4cb662`; `product_code_digest 1d3e9f59…85df7`), byte-identical to the branches' fork point `cae2f67` over `runtime/ cli/ tests/ framework/ capabilities/ migrations/ tools/ fixtures/ bin/ scripts/ Cargo.*` |
| Merged | `phase2/repair-1-r4-ws01` `d1487e8` (P2-AR-0042, the BC-P2-02 evidence map) as merge **`5ab06b6`**; `phase2/repair-1-r4-residual-c` `854980c` (P2-AR-0043 residual IPs + P2-AR-0053 continuation + P2-AR-0055's OD-P2-03 implementation) as merge **`c38a406`**. Both `--no-ff`, in that order. **Neither merge had a conflict**, and no edit was made inside a merge commit (`git show --cc` is empty for both) |
| Integrated product tip | **`e9a2f9c15c27cdb88a5d43c0f003ce1c3b7b9740`**. `product_code_digest e6332fc7d5af5c73adbe0f200003db30fe5a6fd0b7f24d047d3e340e6f972220`. `governed_state_digest 3d2aeba2fc3b52a95c369c49a854bb9d443b0b03da1180db5339f01d892620c0`. Release `gov` sha256 `e7059b9240d74d384370a56ba8d3306a87f736607ad862e58afc93be49da839c`. Every suite, probe and R1 run below was made at `e9a2f9c` with a clean product tree |
| Verdict | **`READY_FOR_INDEPENDENT_CAPABILITY_VERIFICATION`**. `cargo build --release` 0 warnings, and 0 warnings on a forced debug build of every test target. `cargo test --lib` **276/0**; `cargo test --test certification` **207/0/0 ignored** (fourteen chunks, union = the full list, 207 = 207). Python plugin tests 4/4. rustfmt clean. **`gov contract verify` → `CONTRACT_SOURCE_BOUND`**, 101 capabilities, 798 owners, 0 deferred. All four R1 held-out suites at their recorded baselines, 0 §6 violations in every activity. Both builders' probes reproduce their own records. Nothing was stopped |

This is an integration builder's record. It grades no repair and claims no capability class. Every result below is
regression evidence (Contract v3 O3). Acceptance belongs to the fresh independent verifiers who grade this tree.

---

## 1. Merges

| Merge | Branch (tip) | Conflicts | Notes |
|---|---|---|---|
| `5ab06b6` | `phase2/repair-1-r4-ws01` (`d1487e8`, P2-AR-0042) | **none** | product digest after this merge equals P2-AR-0042's own (`d0c6a0d4…a4c9`) |
| `c38a406` | `phase2/repair-1-r4-residual-c` (`854980c`, P2-AR-0043/-0053/-0055) | **none** | the merges-only tip; `product_code_digest 30ee6e9a…835f` |

Both branches fork from `cae2f67`, whose product tree equals the base's. The two files the handoff flagged as
overlapping merged as the union of both sides' intent, with no textual conflict:

- **`cli/src/main.rs`** — P2-AR-0042 appended the `ContractCmd::Matrix` variant, its dispatch arm and its `g0_label`
  arm; the residual branch changed two existing `IndexOptions` lines (`propagate_direct_changes: true` on
  `gov rebuild-memory` and `gov memory rebuild`) and one help string. Both are in the merged file.
- **`runtime/src/orchestration/control.rs`** — P2-AR-0042 added `outside("contract matrix", …)` to `COMMAND_GUARDS`;
  the residual branch edited one comment line (the skill-bindings location). Both are in the merged file.

**Every new or changed subcommand is classified.** The only new CLI surface in either branch is `gov contract matrix`,
and it carries its `g0_label` arm and its `COMMAND_GUARDS` entry (`outside`, canonical-repository tooling that opens no
governed project — the same class as `contract verify`/`compile`). The residual runs added **no** subcommand: every path
they changed runs under an existing label. `ws03::every_cli_command_label_is_classified_by_g0` passes at the integrated
tip (chunk `cert-c08`), and so do the `control.rs` unit tests (`cargo test --lib`).

Straight after the merges the tree already builds and the contract binds; see §2.

`evidence/merge-and-change-log.out` holds the graph, both merges' parents and their (empty) `--cc` output.
`evidence/identity-and-scope.out` shows that the merges brought in only files the two branches changed, that no
protected path changed, and that every test function of both branches is present at the tip.

## 2. Every change beyond the merges

**One commit**, `e9a2f9c`, and it is the integration-critical reconciliation the handoff names.

| Commit | Files | Change | Why |
|---|---|---|---|
| `e9a2f9c` | `release/capability-baseline/repair-1/r4-ws01/evidence/mapping/owner-spec.yaml` (+64 lines, purely additive, under a labelled comment); then, written by the product from it, `tests/governance/capability-evidence-map.yaml`, `framework/contracts/contract-source.lock`, `docs/generated/GOVERNANCE_CAPABILITY_ACCEPTANCE.md` | 36 evidence-owner entries for the **19 tests the residual branch added** (14 certification, 5 lib), across 14 capabilities | **IP-R4-WS01-3 / R4-IP-2** (§3). The handoff: "map the residual run's new tests to the capabilities their own report names" |

No Rust file, policy, schema, kernel file, migration or test changed after the merges. The owner-spec file belongs to
P2-AR-0042's evidence directory; editing it is the route P2-HO-0049 and P2-AR-0042's own IP-R4-WS01-3 prescribe, and it
is the **only** file outside `integration-4/` that this integration wrote (`evidence/identity-and-scope.out`). Nothing
under `release/verification/`, `release/root-of-trust/`, `release/releases/`, `release/orchestration/phase-1/` or
`release/capability-baseline/audit-0/` changed, and Contract v3 and its canonical import are byte-identical
(`4c2df291…5ed3`).

## 3. The integration-critical item: the evidence map against the residual branch's tests (IP-R4-WS01-3)

**`gov contract verify` returned `CONTRACT_SOURCE_BOUND` straight after the two merges, before any edit**
(`evidence/contract/verify-after-merges.json`). No route through `owner-spec.yaml` was needed to make it pass: the
residual branch renamed nothing, removed nothing and `#[ignore]`d nothing, so none of the map's 441 test owners became
unresolved. The one lib test the residual branch replaced
(`verification::reporting::tests::a_coverage_gap_is_confirmed_unless_every_line_is_held_with_its_heading_markers`) kept
its name, which is what the resolver reads. The map's derived fields also stayed exactly derived: the residual branch's
changes to `scheduler/catalogue.rs` (remedy declarations) and `verification/currency.rs` (two path patterns added to
existing classes) change no check's tiers and no check's input **classes**, which is what the freshness triggers derive
from.

What *was* missing is **R4-IP-2**: the 19 new tests owned no capability. The handoff routes that to this integration, so
I did it by P2-AR-0042's documented route and nothing else:

1. 36 owner entries appended to `owner-spec.yaml`, each under a comment naming this run and the report that routes it.
   Nothing existing was changed or removed.
2. `python3 release/capability-baseline/repair-1/r4-ws01/evidence/mapping/apply_owner_spec.py .`
3. `gov contract compile` — which is what wrote the map, the source lock and the generated view. None was hand-edited.

**The capabilities are the ones the residual reports themselves name** (P2-AR-0043 §7 R4-IP-2, P2-AR-0053 §5,
P2-AR-0055 §9), not capabilities of my choosing:

| New test | Capabilities it was mapped to |
|---|---|
| `r4_residual::a_plugin_registered_inside_a_claimed_task_closes_on_its_os_proposed_change_transaction` | K3 (4,5), F4 (2,5) |
| `r4_residual::a_registration_change_approved_without_its_execution_approval_writes_nothing` | F4 (1,5), K2 (8) |
| `r4_residual::a_direct_upstream_change_observed_at_an_index_rebuild_is_propagated_there_once` | W6 (1,2), O5 (2 — the G1 mutation tier) |
| `r4_residual::the_t2_binding_status_is_reported_…_is_disclosed` | S6 (1) |
| `verification::reporting::tests::binding_status_findings_raise_an_unhonoured_authority_and_disclose_machine_scope` (lib) | S6 (1) |
| `r4_residual::a_repository_contract_rule_that_never_decides_is_reported` | B1 (3), B2 (5) |
| `r4_residual::skill_bindings_are_written_where_they_belong_and_a_legacy_file_moves_on_the_next_write` | B1 (4), B3 (1,2) |
| `r4_residual::an_update_moves_the_tracked_os_stores_and_a_rollback_restores_the_previous_layout` | S5 (3,8; class *migration/rollback evidence*), B3 (3) |
| `migrations::framework::tests::relocate_os_stores_moves_tracked_stores_bytes_unchanged_and_only_them` (lib) | S5 (3) |
| `r4_residual::declared_model_and_runtime_artefacts_are_part_of_the_retrieval_profile_identity` | D4 (1,2), D5 (5) |
| `r4_residual::the_remediation_handoff_stays_available_under_the_block_it_repairs` | L4 (1,2), O5 (13) |
| `scheduler::tests::proposals_and_handoffs_are_refused_by_what_they_rely_on_and_admitted_when_they_remedy` (lib) | L4 (1,2), O5 (13) |
| `r4_residual::a_tool_installed_inside_a_claimed_task_closes_on_its_os_proposed_change_transaction` | F3 (4,5,7), F4 (5), K3 (4,5) |
| `r4_residual::an_installation_change_approved_without_its_installation_approval_writes_nothing` | F3 (4), F4 (1,5), K2 (8) |
| `cit::materiality::tests::a_tool_installation_descriptor_is_a_governance_and_a_security_change` (lib) | K3 (4,5) |
| `r4_residual::a_tool_installation_is_gated_for_each_way_it_expands_authority` | F3 (2,4), F4 (1,5), K3 (4,5) |
| `r4_residual::ordinary_allowlisted_network_use_does_not_gate_but_a_new_boundary_does` | F3 (4), F4 (5) |
| `r4_residual::an_installation_whose_envelope_changed_after_simulation_is_refused_at_the_write` | F3 (4), F4 (5), K2 (8) |
| `tools::tests::the_os_reads_an_installations_own_commands_for_what_it_would_hold` (lib) | F4 (1) |

**`gov contract verify` at `e9a2f9c`** (`evidence/contract/verify-final.json`): `CONTRACT_SOURCE_BOUND`; 101
capabilities; **798 owners** (was 762), `test` 477 (was 441) and every other kind unchanged; **0 deferred**, nothing
absent from the tree; 76 capabilities keep a G-tier owner; the same **16** capabilities are owned only by tests;
checklist items naming an owner **587** of 713 (was 586). So P2-AR-0042's disclosed gaps are unchanged in kind and one
item smaller (§7).

Three independent checks that the chain is still sound after the edit, all on the integrated tree:

- `contracts::tests::the_committed_binding_chain_verifies` and the other 22 `contracts::tests` pass (`--lib`);
- the four `ws01r4` certification tests pass, including `gov_contract_verify_enforces_the_evidence_owners` and
  `the_owner_resolver_lists_exactly_the_tests_the_certification_harness_runs`;
- P2-AR-0042's own mutation controls give **29/29** against my committed chain, and its control 29 shows that
  `gov contract compile` over it rewrites the evidence map **byte-identically** (AC-13). The round-1 BC-P2-01 controls
  give **20/20** (§6.3).

**No owner was deleted and no test was renamed, removed or `#[ignore]`d.** The tip lists 207 certification tests with 0
ignored and 276 lib tests with 0 ignored (`evidence/identity-and-scope.out`).

## 4. OD-P2-03 integrated, not re-litigated

OD-P2-03 ("gate only elevated installs") is in force and settled by the product owner. P2-AR-0055's implementation is
merged exactly as it stands; this integration changed nothing about it, argued nothing about it and added no test to it.
What the integrated tree shows:

- `r4_residual::a_tool_installation_is_gated_for_each_way_it_expands_authority`,
  `ordinary_allowlisted_network_use_does_not_gate_but_a_new_boundary_does` and
  `an_installation_whose_envelope_changed_after_simulation_is_refused_at_the_write` pass at the tip (chunk `cert-c14`),
  as do `ws07::a_governed_security_review_by_another_role_lets_the_installation_proceed` and
  `ws07::a_tool_installation_is_approved_only_for_that_installation` (chunk `cert-c12`);
- WS-7's own round-3 named checks, run **unedited** on the integrated binary, report `W7R3-41.a HOLDS — IP-W7-1
  confirmed: the OS-sealed report closing a security task by another session and role is the governed review; the
  install proceeds with **no owner gate**`, and `W7R3-41.b HOLDS` (a self-attested review does not). That is OD-P2-03's
  non-gated branch and its fail-closed condition, measured by a probe written before the decision (§6.2);
- the R4-O1 probe's own gated installation (a descriptor that fails a condition) still closes inside a claimed task on
  its change transaction's writes (§6.2);
- the six authority-expansion triggers, the envelope's sources and the fail-closed rule are policy data
  (`CHANGE_POLICY.change_classes.tool_installation`, `TOOL_POLICY.installation_envelope`,
  `tools/registry/TOOLS.yaml network_allowlist`) with the governed record `spec/decisions/D-0011.yaml`, all merged
  unchanged.

I did not add owners to the evidence map for OD-P2-03 beyond the capabilities P2-AR-0055's own R4-IP-2 names (F3, F4,
K3), and I made no claim about whether the implementation satisfies Contract v3 — that is the verifiers' call, and
OD-P2-03 itself says so.

## 5. The suite-to-contract matrix, regenerated on this tree

`gov contract matrix` was run by the integrated release binary from **this run's own outputs** and nothing else
(`suite-to-contract.json` → `run_evidence_supplied`, each with its SHA-256): `evidence/regression/cargo-test-lib.e9a2f9c.out`,
the fourteen `cert-c*.out` chunks, `evidence/r1-heldout/r1-heldout-final-e9a2f9c.out`, and a G5 `gov health run` plus
`gov doctor` on a disposable bootstrap-installed project (`evidence/matrix-inputs/`, produced by P2-AR-0042's own
`tier-runs.sh`, copied byte-identically). The matrix is
`release/capability-baseline/repair-1/integration-4/suite-to-contract.{json,md}`; nothing in it is hand-written.

**Owner census, and how it moved from P2-AR-0042's:**

| Last-run status | P2-AR-0042 (`9bafcb3`) | **Integrated `e9a2f9c`** | Why it moved |
|---|---|---|---|
| `PASSED` (test owners) | 441 | **477** | the 36 owners added for the residual branch's 19 new tests. None failed; none is `#[ignore]`d |
| `RAN` (checks, doctor, held-out) | 174 | **174** | unchanged: 127 governance-family checks RAN at G5 (all ok, executed), 34 doctor checks RAN (33 ok, `doctor:D032` with findings — the disclosed posture of an unprovisioned bootstrap machine, not a defect), 13 held-out suites RAN at their baselines |
| `NOT_IN_SUPPLIED_EVIDENCE` | 37 | **37** | unchanged: the 19 `g0`, 13 `human-gate` and 5 `release` owners; no supplied output records a run of the guard, gate or release command itself |
| `OBLIGATION` | 110 | **110** | unchanged |
| **total** | 762 | **798** | |

All **9** held-out tests named by owners PASSED. The G5 run was HEALTHY with 39 families and none not-ok; `gov doctor`
was DEGRADED with `D032` as its only failing check.

## 6. Regression

### 6.1 Suites (`evidence/regression/`)

| Suite | Result | Evidence |
|---|---|---|
| `cargo build --release` at `e9a2f9c` | **0 warnings** | `cargo-build-release.e9a2f9c.out` |
| forced debug build of `runtime`, `cli` and every test target | **0 warnings** | `warnings-check.e9a2f9c.out` |
| `cargo test --lib` | **276 passed / 0 failed / 0 ignored** = 262 (round-3 integration) + 9 (P2-AR-0042) + 5 (residual: 3 + 1 + 1) | `cargo-test-lib.e9a2f9c.out` |
| `cargo test --test certification` | **207 passed / 0 failed / 0 ignored** = 189 + 4 (`ws01r4`) + 14 (`r4_residual`). Fourteen module chunks, every one at `e9a2f9c` with `dirty=0` in its own header; the union of the chunks equals the full test list (**207 = 207, empty difference**) | `cert-c{01..14}.out`, `cargo-test-certification.SUMMARY.out`, `cert-test-list.txt`, `cert-passed-union.txt`, runner `cert-chunk.P2-AR-0054.sh` |
| Python plugin tests (`capabilities/tests`) | **4 passed** | `python-plugin-tests.e9a2f9c.out` |
| rustfmt (edition 2021) `--check` | this integration changed **no** Rust file. Over every Rust file the two branches changed, `--check` is clean; the only `rc=1` is `tests/certification/main.rs`, whose 36 hunks are all in the child modules `section6.rs` and `srr.rs` that rustfmt follows from it and that neither branch nor this integration touched — the same two files, with the same hunks, that the round-3 integration and both round-4 builders recorded | `rustfmt-check.out` |
| `gov contract verify` | **`CONTRACT_SOURCE_BOUND`** (§3) | `evidence/contract/verify-final.json` |

`export CARGO_BUILD_JOBS=2` for every build. No `GOV_*` variable was set for any suite (the chunk runner and the R1
runner both strip them).

### 6.2 R1 held-out suites — all four, unedited, private path (`evidence/r1-heldout/`)

The runner is P2-AR-0055's, changed only in the run id, the private scratch root, the S1 copy's name, the worktree path
and two header lines (the diff, after substituting the run id back, is exactly those header lines — shown in the
command that produced it). The four suites are copied byte-identically into the private, uniquely named root
`<worktree>/target/P2-AR-0054/r1-P2-AR-0054-private`; `cmp` records **26 `identical` lines**; the expected checkout
names `wt/srr1-r1-verify{,-2,-3,-4}` are symlinks to **this** worktree only; the suites run against this tree's own
debug `gov`. Run at `e9a2f9c` with 0 product files differing from HEAD.

| Suite | Baseline | **Integrated `e9a2f9c`** | Failing tests (identical to the baselines) |
|---|---|---|---|
| AR-0027 | 26/3 | **26/3** | `heldout_srr2` b1, b2; `heldout_srr3` d3 |
| AR-0029 | 26/2, `ho_f` does not compile | **26/2**, `ho_f_preservation` does not compile | `ho_b` b3, b6 |
| AR-0031 | 27/7 | **27/7** | `hx_a` a1, a5, a8; `hx_b` b6; `hx_c` c2, c3; `hx_d` d2 |
| AR-0033 | 30/1 | **30/1** | `hv_a` a1 only — the size pin (84 files / 740 functions) |

Every suite is exactly at its recorded baseline, failing test for failing test.

- **Census** (AR-0033 `hv_a::a1`'s own independent walk of this tree): **123 files, 2392 functions**. That is exactly
  the union: the round-3 integration had 123 / 2304; P2-AR-0042 added 36 functions (`contracts.rs`, measured 2340) and
  the residual branch added 52 (measured 2356); 2304 + 36 + 52 = 2392, with no file added or removed.
- **S1** — AR-0033's census with only its two size assertions **printed** instead of asserted, in the labelled copy
  `hv_a_derivation.a1-unpinned.P2-AR-0054.rs.txt` (byte-identical to P2-AR-0055's, P2-AR-0053's, P2-AR-0043's,
  P2-AR-0042's, P2-AR-0041's and P2-AR-0032's; its printed label still reads P2-AR-0032, `cmp`-verified). It
  **passes**, so `hv_a::a1` is judged on its property, which holds. Per activity (derived / writers / exempt /
  **violations**): human_gate_create 50/45/1/**0**; human_gate_approve 1/1/0/**0**; release_certification 1/1/0/**0**;
  trust_policy_mutation 8/1/0/**0**; privileged_plugin_acquisition 13/3/0/**0**; floor_lower_or_reset 4/1/0/**0**;
  present_below_floor_release_as_current 1/1/0/**0**. These are P2-AR-0055's numbers exactly: P2-AR-0042 added no §6
  writer, so the union's §6 shape is the residual branch's.
- **S2** — AR-0033's own `derive.py` with only its ROOT line substituted: the same census (123 / 2392) and **0
  violations** in all three splitter configurations (indentation or brace-depth, with and without the `cfg(test)`
  cut). Under the indentation splitter privileged_plugin_acquisition reads 12/2 rather than 13/3, the
  function-boundary difference P2-AR-0055 recorded; violations are 0 either way.
- **Failure messages** — the normalised failure and panic messages of the four unedited suites are **identical to both
  merged branches' own final runs**: 42 lines each, empty diff against P2-AR-0042's run at `9bafcb3` *and* against
  P2-AR-0055's at `4bd7468` (`failure-messages-vs-branches.txt`), and so transitively identical to the round-3
  integration's.
- **R1-sensitive surfaces.** No file under `runtime/src/srr/` differs from the base. The §6 sinks the branches touched
  (`capabilities/governance.rs::register_write`, `tools.rs::install_write`, both asking the acquisition sink at the
  instant of their write) are merged unchanged, and `section6::both_capability_acquisition_primitives_ask_section_6_without_consulting_the_descriptor`
  passes at the tip (chunk `cert-c05`).

### 6.3 Both builders' own probes on the integrated binary (`evidence/builder-probes/`)

Every probe of record was run **unedited** from its own evidence directory against the integrated release `gov`
(`e7059b92…`); the residual branch's labelled derived copies were run as they are. Output was written only under
`evidence/builder-probes/`.

| Builder / probe | The builder's own record | **Integrated, unedited** | **Integrated, labelled derived copy** |
|---|---|---|---|
| P2-AR-0042 `owner-mutation-controls.py` | 29/29 as expected | **29/29** — including control 29: `gov contract compile` over the committed chain rewrites the evidence map byte-identically | — |
| P2-AR-0042 → round-1 `ws01-12/.../bc-p2-01/mutation-controls.py` | 20/20 with the round-1 codes | **20/20**, same codes | — |
| P2-AR-0042 `planted-faults.py` | 20/20 detected across 18 gates | **20/20 detected across 18 gates** (A, B, C, D, F, G, H, I, J, K, L, M, N, O, R, T, U, W). M1, T3 and W7 report the fault as a warning-level finding while the check stays ok, exactly as recorded | — |
| P2-AR-0042 `release-tamper.py` | as written ok; tampered `ok false`, `modified [KERNEL.yaml]` | **the same**, and the `release build` it runs first reports `capability_contract = CONTRACT_SOURCE_BOUND` on the integrated chain | — |
| P2-AR-0042 `product-mutations.sh` | 5/5 (control PASSED, mutant FAILED) | **5/5**: each of the five owners PASSED on the unmutated copy and FAILED on the mutant, and every mutation reverted `identical-to-HEAD` (E1 `authority`, V1 the oracle schema, W3 `context::manifest`, P1 `greenfield` via `observability`, Q4 `upstream`) | — |
| residual → WS-7 `ip_task_close_registration.py` (INT3-O1) | unedited: close refused `MATERIAL_CHANGE_REQUIRES_CIT`; derived: registered, `CIT-0001` COMMITTED, close DONE | **unedited: close refused `MATERIAL_CHANGE_REQUIRES_CIT`** for `governance/project/plugins/p1.yaml` (`security_change` and `governance_change`) — the helper answers only the first gate, so no change control happened | **`registered: True`; `CIT-0001` COMMITTED, `origin: system`, kind `plugin-registration`, triggers `[governance_change, security_change]`, radius R5; approval gate HDG-0001 and execution gate HDG-0002 naming each other; CIT-E's writes cover the descriptor; close ok True, task DONE** |
| residual → WS-7 `ws07_r3_named_checks.py` (INT3-O1) | unedited: 2/11, 5 controls BROKEN; derived: 11/11, every control holds | **2 of 11 discriminating checks PASS, exactly 5 controls BROKEN** (31.setup, 31.c, PC.c, PC.g, PC.f) | **11/11, every control HOLDS** |
| residual → P2-AR-0053 `tools_install_task_close.py` (R4-O1) | after the change: O1 and O2 both close DONE; `CIT-0001` COMMITTED, `origin: system`, kind `tool-installation`, triggers `[governance_change, security_change]`, R5 | **O1 and O2 both close DONE** (`close ok: True`, no refusal); `CIT-0001` COMMITTED, `origin: system`, trigger/effective trigger `security_change`/`governance_change`, R5, `record_seal: VERIFIED`; O3 (control) installs with nothing to close | — |

**No integration regression was found**: every line either builder recorded on its own branch reproduces on the
integrated tree, in the same direction, including the two probes that are *meant* to fail unedited (WS-7's IP probe and
named checks, whose helper answers only the first gate — P2-AR-0043's R4-IP-1, and the reason the labelled derived
copies exist).

## 7. P2-AR-0042's disclosed gaps, after the integration

Recorded, not closed. The integration changed none of them in kind:

1. **16 capabilities owned only by builder regression tests** — C5, F5, G1, H3, K3, M2, M3, N2, Q2, Q3, Q4, R2, T2, V1,
   V2, V3. Unchanged: the owners I added are tests, and they went to capabilities that (except K3) already have tier
   owners. `gov contract verify` reports the list itself.
2. **25 capabilities with no G-tier owner**, 9 of which have a human-gate, release/clean-clone or held-out owner.
   Unchanged: `capabilities_with_a_tier_owner` is still **76**.
3. **No G6 (`gov health qualify`) owner.** Unchanged — IP-R4-WS01-4 remains open.
4. **Checklist items naming no owner: 126 of 713** (was 127). One item (B2.5's neighbourhood, B1.3) gained an owner
   through the mapping above. Per-item claims are builder claims — and the 36 I added are an *integrator's* claims; a
   verifier should sample them like any other.
5. Unit-level-only invalidation proofs for the schema, migration and security/sensitivity freshness triggers;
   `severity` `null` for all 101 capabilities; `contract_binding` not mapped to a capability; owners that only guard a
   command's authority removed in P2-AR-0042's review — all unchanged.

## 8. Carried forward, not closed: integration points and observations for the verifiers

**From P2-AR-0042 (`r4-ws01/00-REPAIR-REPORT.md` §11), all still open:**

| Id | For | What |
|---|---|---|
| IP-R4-WS01-1 | WS-2 | add `contracts::owner_sources_fingerprint(root)` to the `contract_binding` cache key, so a cached green family cannot survive a renamed or ignored owner test |
| IP-R4-WS01-2 | WS-2, WS-8 | carry `evidence_owners.deferred` / `not_in_this_tree` into the G5 family detail and `PRE_RELEASE_CHECKS.json` |
| IP-R4-WS01-3 | this integration and every later builder | **acted on here** (§3): after merging, `gov contract verify` passes and the new tests are mapped. The obligation stands for every later change: renaming, removing or `#[ignore]`ing one of the now-**477** mapped tests fails `gov contract verify`, `contracts::tests::the_committed_binding_chain_verifies`, the `contract_binding` family and `release build` |
| IP-R4-WS01-4 | WS-2 | a test or run of `gov health qualify` with a FORMAT_SAMPLE oracle, so G6 owners for V1–V4 (and W12.7) can be mapped |
| IP-R4-WS01-5 | WS-2 and the owning workstreams | tier owners for the 16 test-only capabilities |
| IP-R4-WS01-6 | WS-2 | `index_freshness` did not report an edited `README.md` on a minimal project while it did report an edited `src/lib.rs`; recorded, not judged |

**From the residual reports (P2-AR-0043 §7, P2-AR-0053 §5, P2-AR-0055 §9):**

| Id | For | What |
|---|---|---|
| R4-IP-1 (**as revised by P2-AR-0055**) | verifiers and probe authors | a probe that registers an **executable plugin** must answer **both** its gates (the execution gate and the registration's change-transaction gate) or nothing is registered. For a **tool installation**, OD-P2-03 revises the earlier note: a review-evidenced installation **inside** the authorised envelope raises **no** gate and completes in one request; one that expands authority, or fails one of the five conditions, raises the change gate and must be answered. Both halves are visible in §6.3: WS-7's probes unedited show the plugin half, and `W7R3-41.a` unedited shows the tool half |
| R4-IP-2 | WS-1 evidence map | **acted on here** (§3) for all 19 tests the residual runs added. It is not "closed": the per-item owner claims are mine as integrator, and the reports' mapping is the source I followed |
| R4-O1 | — | closed by the owner (OD-P2-03) and implemented by P2-AR-0055; merged here unchanged (§4) |
| R4-O2 | routing / verifier | `gov plugins unregister` still writes the sealed registry directly, not through a change transaction, and **nothing uninstalls a tool**, so there is no de-installation path to govern. Whether K3 wants impact simulation for removal is not stated by the sources, and OD-P2-03 does not speak to it. Unchanged here |
| R4-O3 | WS-8 (probe maintenance) | WS-8's `r1-invariants.sh` line `floors_path( outside state.rs = 1` stays at 1 (INT3-O3 not done, by P2-AR-0043's reasoning that touching `srr/state.rs` is not cheap and safe). Unchanged here |
| R4-O4 | routing (WS-9) | **checked, not closed** (`evidence/carried-items/r4-o4-and-r4-o5-checks.out`): `cit` schema is 1.3.0 in both `framework/schemas/cit.schema.json` (`x-schema-version`) and `framework/KERNEL.yaml`, with **no** drift for any schema; `framework/schemas` is a kernel `payload_dir`, so `gov update` delivers the new vocabulary with the kernel; `install_tool` is additive (an older transaction never carries it); and `M-4.1.5-4.1.6` carries the round-4 migration surface (`relocate_os_stores` before `require_index_rebuild`), proven end to end from 4.1.1 by `r4_residual::an_update_moves_the_tracked_os_stores_and_a_rollback_restores_the_previous_layout`. The routing question — whether WS-9 wants anything more for adopted projects — stays open |
| R4-O5 | routing (optional) | **checked, not closed** (same file): `CHANGE_POLICY` and `TOOL_POLICY` carry their own `version: 1.1.0`, which is **not** a schema version — `KERNEL.yaml` declares `policy-CHANGE_POLICY`/`policy-TOOL_POLICY` **1.0.0**, the versions of the policy *schemas*, and no schema file changed, so `kernel::schema_version_problems` finds no drift (`arch` passes). Policies ship as kernel payload, so an update replaces them wholesale. A project still on an older kernel has neither new key, and the code fails closed there: `TOOL_POLICY.installation_envelope` absent → `undetermined` → treated as an expansion; `CHANGE_POLICY.change_classes` absent → `class_decision` returns `Null` → gated exactly as before. So every installation gates until the project updates, which is the intended default and needs no migration. The optional suggestion — noting the policy-version bump in the release manifest — is not done |
| R4-O6 | verifier (optional) | a read-only `gov tools envelope --descriptor f` (or `--dry-run`) so an auditor can inspect an installation's envelope verdict without proposing a transaction. Not done: OD-P2-03 does not require it and it would add a subcommand to classify |
| INT3-O4 | verifier | legacy unsealed task/CIT records rewritten by `gov` inside a claim window are **reported** (`os_managed_unbound`), never blessed, and stay unsealed until a governed re-issue. Carried from integration-3, not reopened |
| R3-WS5-11 | WS-5 | the sandbox `memory_retrieval_regression` symbol route: not reproduced by the round-3 integration, not reopened here. Carried |

**Also carried, unchanged, from P2-AR-0043 §5 (four optional items it did not do, each with its reason):** INT3-O3,
IP-R3-WS04-03, IP-R3-WS04-06, IP-R3-WS02-11.

## 9. Contradictions and stopped items

**None.** No item was stopped. The two branches did not contradict each other: they touched disjoint product surfaces
apart from the two files in §1, both of which merged as the union. No refusal a repair-delta class requires was
reopened, no check, schema or test was weakened, no default role, unauthenticated answer path or standalone human-gate
anchor was introduced, and there is no signing inside `gov`. The availability rule holds as both builders left it: this
integration added no guard, no finding and no block.

## 10. What I did not do

I did not grade any repair, claim any capability class, or mint the candidate — `cap2-candidate-1` is minted by the
orchestrator from this tip. I did not re-litigate OD-P2-03, did not change any product code, and did not open any
round-5 work. I did not do IP-R4-WS01-1/-2/-4/-5/-6, R4-O2, R4-O3, R4-O6 or any optional item (§8). I changed no probe
of record: every derived copy that was run is the branch's own labelled file, run as it stands.

## 11. Evidence index (`evidence/`)

| Path | What |
|---|---|
| `identity-and-scope.out` | digests of the base, both branch tips, both merges and the tip; merge parents; release binary; Contract v3 and frozen-contract sha256; protected-path and scope checks; the test census at the tip |
| `merge-and-change-log.out` | the commit graph, both merges' parents and their (empty) `git show --cc`, and the one commit after them |
| `contract/` | `gov contract verify` after the merges and at the tip; `gov contract compile`; the owner-spec diff |
| `regression/` | release build, forced-warnings build, `--lib`, the fourteen certification chunks with the runner, the test list, the passed-union and the summary, Python plugin tests, rustfmt |
| `r1-heldout/` | runner copy, S1 labelled copy, `failure_messages.py`, the run output (byte identity, per-suite summaries, census, S1, S2) and the failure-message comparison against both branches |
| `builder-probes/` | the runner, `unedited/` and `derived-runs/` outputs of both builders' probes |
| `matrix-inputs/` | `tier-runs.sh` (byte-identical copy), the G5 health run, `gov doctor`, `init`/`rebuild-memory`, the provenance line and the `gov contract matrix` result |
| `carried-items/` | the R4-O4 and R4-O5 checks the handoff asks the integrator to make |
| `../suite-to-contract.{json,md}` | the regenerated matrix (product output, in the run directory beside this report) |

## 12. Process disclosures

- Model: Claude Opus 5 (1M context), `claude-opus-5[1m]`. Fresh context for this run. No sub-agents were used and the
  owner was not contacted. I read no session or agent transcript, no task-output store and no user auto-memory.
- `rm` is denied in this environment and was not used. Nothing had to be moved aside: no superseded evidence was
  produced, and my scratch trees are under `target/P2-AR-0054/`.
- The certification suite was chunked because a full run exceeds the tool's ten-minute foreground limit. Every chunk
  ran at `e9a2f9c` with `dirty=0`, and the union of the chunks is the full test list.
- One long probe (`product-mutations.sh`, which compiles a mutated copy of the tree once per case) was started with
  `nohup` writing to my own files, which I read; the task-output store was not read. A foreground loop that polled for
  its exit was itself moved to the background by the harness after ten minutes — its `pgrep` pattern matched the
  polling command's own command line, so it never saw the probe exit. Its task-output file was **not** read; the
  probe's completion was read from its own output file, which records `# done 2026-09-20T19:34:33Z` and all five
  cases.
- The machine may have been shared with other work during the runs; timings are indicative only.
