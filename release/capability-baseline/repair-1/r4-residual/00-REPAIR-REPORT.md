# P2-AR-0043: repair iteration 1, round 4, residual integration points

| Field | Value |
|---|---|
| Run | P2-AR-0043, role `capability-repair`. Model: Claude Opus 5 (1M context), `claude-opus-5[1m]`. Fresh context |
| Handoff | P2-HO-0042 (round 4, residual integration points). Rules from P2-HO-0031 (availability rule), P2-HO-0020 and P2-HO-0010. Adjudications P2-ADJ-0001/-0002/-0003. Owner decisions OWNER-DECISION-P2-0001/-0002 |
| Branch / base | `phase2/repair-1-r4-residual`, from `cae2f67`. Its product tree is the round-3 integrated tree (merge `e4cb662`; `product_code_digest 1d3e9f59…5df7`, equal to integration-3's product tip) |
| Work commits | `e752bed` (INT3-O1, INT3-O2, IP-W7R3-10), `00615f1` (binding status, shadowed rules, heading-marker retirement, skill bindings and registry relocation, TOOL_PERMISSIONS, remediation handoffs), `e5336d9` (profile identity, docs and help text, `gov status` sealing scope), `3a384d8` (§6: the registration writer carries the signature and asks the sink), `34e3725` (a WS-4 round-2 test follows INT3-O2). Then the commit that adds this report, `claims.yaml` and `evidence/` (no product file) |
| Product identity | at `34e3725`: `product_code_digest 1eb1564c0ec4d4c2bb0d5630a5dc9de896f77d4771b8227a7997e096d28d9a87`, `governed_state_digest a700ee0d…fc96`. Release `gov` sha256 `512913ef…1112` |
| Verdict | **`READY_FOR_INDEPENDENT_CAPABILITY_VERIFICATION`**. Every routed item is claimed. No owner decision is needed. Four optional items are not done, each with its reason (§5) |

Everything here is builder evidence (Contract v3 O3). Nothing in it is an acceptance, and I grade no one's work, my own included.

---

## 0. Regression and R1 (at the final product commit)

| What | Result | Evidence (`evidence/…`) |
|---|---|---|
| `cargo build --release` | 0 warnings | `regression/cargo-build-release.34e3725.out` |
| debug build + every test target (lib and main forced to recompile) | 0 warnings | `regression/warnings-check.34e3725.out` |
| `cargo test --lib` | **265 passed / 0 failed** (262 at the base; +3 new; 1 replaced under its name) | `regression/cargo-test-lib.3a384d8.out` (the tree differs from `34e3725` only in `tests/certification/ws04r2.rs`) |
| `cargo test --test certification` | **198 passed / 0 failed / 0 ignored** (189 at the base; +9 new). Run in nine module chunks (each under the tool's 10-minute limit). The union of the chunks is the full test list (198 = 198, empty difference) | `regression/cert-c{1..9}.*.out`, `regression/cargo-test-certification.SUMMARY.out`, runner `regression/cert-chunk.sh` |
| Python plugin tests (`capabilities/tests`) | 4 passed | `regression/python-plugin-tests.34e3725.out` |
| rustfmt (edition 2021) `--check`, each changed Rust file alone | clean. `tests/certification/main.rs` reports hunks only in its child modules `section6.rs` and `srr.rs`, which I did not touch. The hunks are identical at the base | `regression/rustfmt-check.34e3725.out` |
| R1 held-out suites, all four, unedited, private path | every suite at its recorded baseline (below) | `r1-heldout/r1-heldout-final-34e3725.out`, runner `r1-heldout/run-r1-heldout.sh` |

`CARGO_BUILD_JOBS=2` for every build. No `GOV_*` variable was set for any suite.

**R1 held-out suites** (run unedited through the private root `<worktree>/target/P2-AR-0043/r1-P2-AR-0043-private`; `wt/srr1-r1-verify{,-2,-3,-4}` are symlinks to this worktree; 26 `identical` `cmp` lines; the tree's own debug `gov`):

| Suite | Baseline | This tree `34e3725` | Failing tests (identical to the round-3 integration's) |
|---|---|---|---|
| AR-0027 | 26/3 | **26/3** | heldout_srr2 b1, b2; heldout_srr3 d3 |
| AR-0029 | 26/2, `ho_f` does not compile | **26/2**, `ho_f_preservation` does not compile | ho_b b3, b6 |
| AR-0031 | 27/7 | **27/7** | hx_a a1, a5, a8; hx_b b6; hx_c c2, c3; hx_d d2 |
| AR-0033 | 30/1 | **30/1** | hv_a a1 only: the size pin (84 files / 740 functions) |

- **Census** (AR-0033 `hv_a::a1`'s own independent walk of this tree): **123 files, 2329 functions** (the round-3 integration had 123 / 2304).
- **S1**, AR-0033's census with only its two size assertions printed instead of asserted. The labelled copy is `r1-heldout/hv_a_derivation.a1-unpinned.P2-AR-0043.rs.txt`, byte-identical to P2-AR-0041's (its printed label still reads P2-AR-0032). It **passes**. Per activity (derived / writers / exempt / **violations**): human_gate_create 50/45/1/**0**; human_gate_approve 1/1/0/**0**; release_certification 1/1/0/**0**; trust_policy_mutation 8/1/0/**0**; privileged_plugin_acquisition 10/2/0/**0**; floor_lower_or_reset 4/1/0/**0**; present_below_floor_release_as_current 1/1/0/**0**.
- **S2**, AR-0033's `derive.py` with only its ROOT line substituted: the same census, and **0 violations** in all three splitter configurations.
- **Normalised failure messages** of the unedited suites (the integration's `failure_messages.py`, copied byte-identically): 42 lines, **identical** to the round-3 integration's run (empty diff). See `r1-heldout/failure-messages-vs-integration-3.txt`.
- **R1-sensitive files touched.** `runtime/src/update.rs`: the update snapshot and rollback also cover `governance/registry/` (§3.7). `runtime/src/capabilities/governance.rs`: the registration writer is the §6 bullet-5 site (§1). No file under `runtime/src/srr/` changed. `guard_acquisition(` is still called only from `capabilities/governance.rs`, which is `hx_a::a6`'s sink-caller set. The registration writer now asks the sink itself at the instant of its write (§1.4).

---

## 1. INT3-O1 (WS-5 × WS-7): a plugin registration inside a claimed task

**Requirement.** Both of these hold.
- **Contract v3 K3** (lines 638–647): impact simulation auto-triggers for material **security** and **governance/policy** changes. A plugin registration is both.
- **Contract v3 F4** (425–431): elevated permissions reference an authoritative gate or decision; the descriptor cannot authorise itself; registration lives in trusted OS state.

So the owner-approved registration does not replace change control. A registration inside a task must end with impact simulation linked (auto-triggered) in a form the close accepts. The worker must not hand-file a change-impact transaction (CIT) the OS could have triggered, and the registration gate must not silently stand in for CIT-P/E.

**Before** (integration-3 record, same product code). `gov plugins register` passed its own owner gate. The task's close was then refused `MATERIAL_CHANGE_REQUIRES_CIT` for `governance/project/plugins/p1.yaml`.

### 1.1 Mechanism: the registration is carried out by a change transaction the OS proposes

`gov plugins register --descriptor d` (`capabilities::governance::register`) does the following.

1. **It derives the request** (`prepare`): schema, health, the implementation binding, the acquisition sink `guard_acquisition` (asked unconditionally), and the registration subject. Nothing is written.
2. **For a new request it proposes the registration's change transaction itself** (`cit::propose_registration`):
   - `origin: system`, `system.kind: plugin-registration`;
   - one manifest operation `register_plugin`, carrying the OS-normalised descriptor, the registration subject and the implementation digest; the content digest the transaction's approval binds covers it;
   - declared trigger `security_change`. Derived materiality (`cit::materiality`): `governance_change` (the descriptor is under `governance/**`) **and** `security_change` (a new rule: a plugin registration path decides which program the OS executes, Contract v3 F4);
   - radius R5 by `CHANGE_POLICY.radius_rules.governance_paths_radius`.

   **CIT-P is simulated automatically** (K3). The simulation brings the index current first, best effort (see §1.3). Under CHANGE_POLICY the simulation raises the transaction's **own gate**, which approves the change.
3. **For an executable plugin it then raises the execution-approval gate**, exactly as before: subject `plugin-registration`, trigger `privilege_elevation`, human-only. This gate's signed package names the transaction, the transaction's gate and its binding digest (`subject.change_transaction`), and its impact text states the simulated impact. The transaction journals the execution gate raised for its subject. **The two approvals name each other.**
4. **Once both are answered, repeating `gov plugins register` approves and executes the transaction** (`cit::execute_registration`): approve from the transaction's gate answer, read through `gates::verified_answer`; then CIT-E. The authority for this step is the registration's own (`register_plugin`, plus `TOOL_PERMISSIONS.install_authority_roles`). The worker therefore needs no L3 CIT roles and files no CIT, and every other CIT check applies unchanged: guards, sealed state, content and impact binding, G0 with the transaction's paths.
5. **Only CIT-E writes the registration.** The `register_plugin` operation calls `capabilities::governance::apply_registration`, which:
   - re-derives the request from the bytes as they are now;
   - requires exactly the approved subject, else `PLUGIN_REGISTRATION_STALE`;
   - re-verifies the execution approval (F4), else `PLUGIN_NOT_APPROVED`;
   - writes the descriptor and the sealed registry entry through the one writer `register_write`, which asks the §6 sink at the instant of its write (§1.4).

   CIT-E records per-path writes. So a registration made inside a claimed task **closes on the transaction's recorded writes** (task close step 10a, `cit_window_writes`). Nothing at the close was changed.

**Neither approval stands in for the other.**
- Answering only the execution gate leaves the registration unwritten; `register` returns the transaction's gate as pending.
- Answering only the change gate and executing the transaction directly (`gov cit approve` / `gov cit execute`, L3) is refused at CIT-E with `PLUGIN_NOT_APPROVED` and **rolled back**. After that, a new request raises a new transaction, because a rolled-back one is finished.
- A decline of either gate ends the request. A declined execution gate also closes the open transaction (REJECTED, sealed). A declined change gate makes `register` report `declined`.
- A revoked change gate is re-raised by re-simulating when the request is repeated. A revoked execution gate stops the plugin as before (F4 at every execution); the committed transaction stays history with its own answered gate, so there is no integrity finding.
- An in-force registration of the same subject by the same gate is `unchanged` and raises nothing.

For an **OS-provided** capability server (no execution approval), the transaction's gate is the only gate.

**Why two approvals and not one combined gate.** I considered one gate that approves both. It needs one of two changes:
- change the CIT verification of which gate may approve a transaction; or
- change the F4 check of which gate may approve a registration subject.

Either way, revoking the plugin's execution approval would then also withdraw the committed change's approval. That makes `change_control_integrity` report a HIGH "COMMITTED without approval" for every revoked plugin, and hard-blocks releases. With two gates, each approval keeps its own meaning and lifecycle, which is the handoff's own example. **The cost**: the owner answers two gates per registration, both raised by the first request and presentable together. The sources leave no trade-off open here (the handoff states that neither requirement is an owner question), so nothing is stopped.

### 1.2 Evidence

- **WS-7's probe `ip_task_close_registration.py`** (`evidence/int3-o1/`, release `gov` `512913ef…`):
  - **Unedited**: its helper answers only the first gate, so nothing is registered, and the close is refused `MATERIAL_CHANGE_REQUIRES_CIT` for the hand-written descriptor (`governance_change` and `security_change`). This is correct: no change control happened.
  - **Labelled derived copy** `ip_task_close_registration.INT3-O1.P2-AR-0043.py`. Its only change: the helper answers every gate the registration raises, plus timing and transaction printouts. Results:
    - `registered: True`;
    - `CIT-0001` COMMITTED, `origin: system`, kind `plugin-registration`, effective triggers `[governance_change, security_change]`, radius R5;
    - CIT-E's writes cover the descriptor's current bytes; the transaction's approval gate is HDG-0001 and the registry's execution gate is HDG-0002;
    - **close ok: True, task DONE**.
  - Timings (release): the first request 0.5 s; the executing request (approve, CIT-E, G4) about 1.9 s.
- **WS-7's round-3 named checks** (`evidence/int3-o1/ws07_r3_named_checks.*`):
  - unedited: 2/11 discriminating checks pass and 5 controls are BROKEN. The helper leaves every registration pending on the change gate;
  - labelled derived copy `ws07_r3_named_checks.INT3-O1.P2-AR-0043.py`: **11/11, every control holds**. Its changes: (a) the helper answers both gates; (b) its WT depth; (c) W7R3-13's own two-step sequence also answers the change gate.
- **Certification tests** (new, `tests/certification/r4_residual.rs`):
  - `a_plugin_registered_inside_a_claimed_task_closes_on_its_os_proposed_change_transaction`: auto-proposed and simulated transaction; both triggers; the gates cross-reference each other; nothing written before both answers; CIT-E writes cover the descriptor; the task closes DONE; a later hand edit of the descriptor inside another task is refused `MATERIAL_CHANGE_REQUIRES_CIT` (bound to content);
  - `a_registration_change_approved_without_its_execution_approval_writes_nothing`: F4 direction, `PLUGIN_NOT_APPROVED` and ROLLED_BACK, then a new transaction; `unchanged` on repeat.

### 1.3 Two generic CIT refinements the registration needed (availability rule; A0-K2-03)

Re-registering the plugin that **is** the pinned embedder, at a new revision, failed inside change control. That is exactly what `ws06::embedder_components_…` and `repair2::plugins_are_governed_…` do. The retrieval profile cannot run until the change completes:
- the query embedder is the plugin being re-registered;
- the pin names the old revision.

I made two narrow refinements.
- **CIT-P**: semantic candidates are advisory; `binding::impact_of` excludes them from the approval binding. A retrieval-profile refusal of the candidate query (the pinned embedder unusable, or not the one the index was built with) is recorded (`impact.semantic_candidates_unavailable`, plus a consequence line), and the graph reach stands. `INDEX_MISSING` is still refused, as before.
- **CIT-E**: A0-K2-03 is already applied to dangling edges ("damage already in the working tree is not attributed to this transaction"). It now also applies to the index itself: when the retrieval profile refused to build the index **before** the manifest as well, the same class of refusal after it is recorded (`propagation.index_refresh`), not attributed to the transaction; the index stays as it was (`index_freshness` keeps reporting it). Any other refresh failure, or a refusal the transaction introduced, rolls back as before.

`ws06` and `repair2` pass with their original property assertions. Their only change is the change gate in the shared helper.

### 1.4 §6 (R1): the registration writer is still a derived §6 site

`section6::both_capability_acquisition_primitives_ask_section_6_without_consulting_the_descriptor` found a real regression in my first cut. Splitting `register` had moved the capability-registry write out of the function holding the §6 signature (`join("plugins")` / `guard_acquisition`), so the derived census no longer saw a writer in `governance.rs`. Fixed in `3a384d8`: the one writer, `register_write` (reached only from CIT-E), composes the plugins directory itself and calls `guard_acquisition` immediately before writing. AR-0033's census: privileged_plugin_acquisition 10/2/0/**0**.

---

## 2. INT3-O2 (WS-2): direct upstream change propagates when the G1 rebuild observes it

**Requirement.** Contract v3 W6 (1128–1136) with O5's G1 (mutation) tier. A direct change observed by an incremental rebuild is a mutation observed at G1, so dependent evidence is marked stale when the change is observed, not only at the next claim. Three constraints: keep the claim-time path, keep it idempotent, and zeta-r `W12-G1-dependency-evidence-invalidated` must pass unedited. IP-R3-WS02-05 allowed either path.

**Change.** New `IndexOptions::propagate_direct_changes`, set by the two host-run builds, `gov rebuild-memory` and `gov memory rebuild`. It is never set inside another governed operation, whose own boundary records its effects. After the build, `memory::indexer::propagate_observed_changes` does the following.
- It passes the write guard of the operation it is, `cit propagate`: kernel trust, break-glass, FREEZE_WRITES and PAUSE.
- **Refused, it is deferred, not forced.** The rebuild stands (it stays available under every control), the detection is reported (`upstream_changes.deferred`, `…detected`), and the next claim or governed build propagates.
- Otherwise it runs `cit::propagation::detect_and_propagate(p, "index rebuild", false)`: one sealed system transaction, with rework generated only when the acting role may create tasks.
- Then it re-runs an incremental build so the index includes the markers.

It is idempotent: an input already propagated is not detected again, so the second rebuild records nothing. The claim-time path (`tasks::claim`) is unchanged. The result is reported as `IndexReport.upstream_changes`.

**Authority choice (stated).** Propagation at a rebuild needs no authority beyond the rebuild's own. The markers are OS bookkeeping authorised by `CHANGE_POLICY.propagation` (no gate), attributed to the detection (`detected_by: index rebuild`). This is the same design `detect_and_propagate` already has for an L1 claim, and rework generation still requires `create_task`.

**Evidence.**
- zeta-r `W12-scheduler-integration`, **unedited**, owner-channel shim, runner `evidence/audit-probes/run-audit-probe.sh` (a copy of integration-3's with only the scratch variable changed): **`W12-G1-dependency-evidence-invalidated` FAIL → PASS**. The integration-3 record was FAIL. Every other line is identical, and the run still stops at G2, as recorded (a claim of a task whose mandatory input is absent).
- The integration's labelled derived copy `g1-claim`: W12-G1 PASS and `DERIVED-W12-G1-next-claim-propagates` PASS. The claim-time path is kept.
- Certification `r4_residual::a_direct_upstream_change_observed_at_an_index_rebuild_is_propagated_there_once`: deferred under FREEZE_WRITES (`FROZEN`), rebuild ok; then propagated by the next rebuild (one system transaction, `detected_by: index rebuild`, dependant `retest_required`, index fresh); idempotent (no second transaction, `cit propagate --dry-run` 0); the same through `gov memory rebuild`.

---

## 3. The remaining builder integration points

### 3.1 WS-3 IP-R3-WS03-6 and WS-8 IP-R3-WS08-3: the T2 binding status in D033 and `os_binding_integrity`

Both now report `t2::binding_status()`.
- `verification::reporting::binding_status_view` goes into the family detail beside `binding_key`, as WS-3 asked.
- `binding_status_findings` raises the following.
  - **Medium**: an installed binding authority that is not honoured now (`authority_error`: expired, revoked by root succession, not delegated, machine not listed), and a bound machine not sealing with the authority's active key (WS-8).
  - **Low disclosure**: a provisioned machine sealing in its own machine scope (WS-3).
  - An unprovisioned machine raises nothing here; `installation_authenticity`/D032 disclose its bootstrap posture.
- `t2_severity_on` states that on a machine **bound** to the owner's authority a `FOREIGN` record was written by a machine the owner did not authorise.
- D033 fails on the medium cases; otherwise it appends the sealing scope (`T2 sealing: portable (…)` or `machine scope (…)`) and any disclosure.
- Tests: lib `verification::reporting::tests::binding_status_findings_raise_an_unhonoured_authority_and_disclose_machine_scope`; certification `r4_residual::the_t2_binding_status_is_reported_and_machine_scope_sealing_on_a_provisioned_machine_is_disclosed` (owner-bound machine: portable, nothing raised; anchor-only clone: machine scope disclosed low, D033 passes, `gov status` scope).
- One builder test changed, `ws08_r3::t2_facts_…` (§4).

### 3.2 WS-3 IP-R3-WS03-7: `capabilities/PROTOCOL.md` registry portability

"A fresh clone re-registers" is replaced. A registration sealed on one of the owner's provisioned machines bound to the owner's T2 binding authority is honoured on the others after a clone or pull; a machine the owner did not authorise does not honour it and re-registers (P2-ADJ-0002). The page also documents the two-approval registration (§1) and the move at upgrade (§3.7).

### 3.3 WS-3 IP-R3-WS03-9: alpha-r A5 control-state path

WS-3 recorded this against probe authors and verifiers. The product keeps the emergency-control state at `.governance-state/control.json` (BC-P2-31), so no product change is needed.
- **Unedited**, alpha-r A5 stops where it reads the pre-BC-P2-31 path (`TypeError` on `None`), as WS-3 recorded.
- **WS-3's labelled derived copy** (`A5-emergency-controls.store-path.P2-AR-0034.py`, run unedited) runs to the end (53 observations, exit 0). Its normalised observations are identical to WS-3's own derived run; only random session ids and durations differ.
- Evidence: `evidence/audit-probes/final/`.

**Status: CONFIRMED** (a probe-premise item).

### 3.4 WS-6 IP-R3-WS06-4 with WS-2 IP-R3-WS02-10: shadowed rules; the heading-marker step retired

- The `path_map_compliance` family (G1, G4–G6) raises one **low** finding per `RepositoryContract::shadowed_rules()` entry, a path-map rule that never decides, naming the rule that overrides it and the contract file as subject. The detail lists them. Certification: `r4_residual::a_repository_contract_rule_that_never_decides_is_reported`.
- **Retired**: `verification::reporting::gap_is_heading_marker_artefact`. WS-6's verifier (`memory::coverage`, chunker 3) compares Markdown headings by their text on both sides and lists every uncovered line, so every gap it reports is confirmed. `index_content_coverage` now treats all reported gaps as confirmed; the `verifier_heading_marker_artefacts` detail field is gone.
- **WS-2's unit test `a_coverage_gap_is_confirmed_unless_every_line_is_held_with_its_heading_markers` is replaced under the same name** (the one replacement the handoff allows). It keeps the same fixture and asserts the property that still holds, through the verifier and the family: headings held with their markers are no gap; the unheld body line is the one confirmed gap, reported medium, naming only `b.md`.

### 3.5 WS-6 IP-R3-WS06-7: `skill-bindings.json` to `governance/registry/` and `OS_STORES`

- New store `skill-bindings` in `paths::OS_STORES`: class `authoritative`, tracked, at `paths::SKILL_BINDINGS_PATH = governance/registry/skill-bindings.json`, with the legacy move from `governance/generated/skill-bindings.json`.
- `skills::bindings_path` resolves through `store_path`. `bindings_read_path` reads the legacy file only while nothing is at the location; reading never moves anything. `relocate_bindings` moves it, bytes unchanged, before every binding write. On a conflict the location is authoritative, and `misplaced_os_state` reports the legacy file.
- The template already classifies `governance/registry/**` as authoritative and os-only; its comment was updated. The paths tripwire (`every_writer_location_is_classified_as_its_store`) now includes the bindings writer.
- Certification: `r4_residual::skill_bindings_are_written_where_they_belong_and_a_legacy_file_moves_on_the_next_write`.

### 3.6 WS-9 IP-R3-WS09-4: TOOL_PERMISSIONS for the independent roles

- The template lists `migration-verifier: [READ_REPO, RUN_TESTS]`, `migration-reviewer: [READ_REPO]` and `memory-verifier: [READ_REPO]`.
- `M-4.1.5-4.1.6` declares the template change (`overlay_template_changes`) and delivers it through its existing `sync_overlay_template` for `TOOL_PERMISSIONS.yaml`.
- The A7 verifier is now authorised by `TOOL_PERMISSIONS.roles.migration-verifier`. The designated-duty fallback still applies to a policy that does not list the role, and is asserted explicitly.
- Two tests updated (§4).

### 3.7 WS-7 IP-W7R3-3 / -5 / -6 / -7 / -9

- **IP-W7R3-3.** The currency class `tools_plugins` lists `governance/registry/plugin-registry.json`, keeping the legacy pattern. `project_skills` lists the new bindings location.
- **IP-W7R3-5: relocate at upgrade; brownfield projects must not lose registrations.**
  - New migration operation `relocate_os_stores` (migration schema 1.3.0, mirrored in `KERNEL.yaml`), in `M-4.1.5-4.1.6` before `require_index_rebuild`. It covers tracked stores only (plugin registry, skill bindings), bytes and seals unchanged: nothing becomes honoured by moving, and on a conflict the location wins. A dry run reports and writes nothing. A machine-local store is refused, because its own writer moves it under its own lock.
  - The **update snapshot covers `governance/registry/`**, and `gov update --rollback` restores it as the snapshot saw it, **including its absence**. So the rollback gives the previous release exactly the layout it reads (the legacy registry comes back with `governance/generated/`). An older snapshot that did not cover the directory leaves it as it is.
  - Tests: lib `migrations::framework::tests::relocate_os_stores_moves_tracked_stores_bytes_unchanged_and_only_them`; certification `r4_residual::an_update_moves_the_tracked_os_stores_and_a_rollback_restores_the_previous_layout`. That test runs 4.1.1 → current: moved at the upgrade with bytes unchanged; the stores survive deleting `governance/generated/`; the rollback restores both legacy files byte for byte and removes the directory the update created.
- **IP-W7R3-6: memory-profile hashing and identity.**
  - (a) `memory::profile::file_id` hashes with `capabilities::binding::content_sha256` (the pin's digest: the running binary by its kept label, every other file afresh in each process). The size-plus-mtime shortcut that reused a digest an earlier process recorded is gone. That shortcut was the defect class WS-7 closed for the pin itself: a same-size rewrite inside one timestamp tick.
  - (b) The model and runtime artefacts a descriptor declares (`binding::declared_paths`, the files the registration binds) are in the component identity. In-repository model artefacts go in the portable model identity (index manifest core, `declared: true`). Machine-local model artefacts and declared runtime artefacts go in the machine digest (`runtime_observed`). The descriptor's `model.id`/`revision` and `runtime.id` are carried.
  - Certification: `r4_residual::declared_model_and_runtime_artefacts_are_part_of_the_retrieval_profile_identity`. `ws06::embedder_components_…` passes unchanged.
- **IP-W7R3-7.** The `plugins registry` help text names `governance/registry/plugin-registry.json`. The arm already showed `registry::report` (IP-W7-4).
- **IP-W7R3-9.** `docs/ARCHITECTURE.md` gives the registry directory (both files) and its template rule, and the store classification including the move at upgrade and the rollback.

### 3.8 WS-4 IP-R3-WS04-11 and -09: block scope for `cit.propose` / `handoff.create`; docs

**Decision** (catalogue documentation table, pinned by a unit test).

| | `cit.propose` | `handoff.create` |
|---|---|---|
| Critical, global (`CRIT_ALL`) | Refused, except a proposal whose subjects reach the block's; that proposal is the block's remedy, and its execution must clear the block | Refused, except the handoff of work that declares the block's check among its `remedies` and whose subjects reach the block's |
| D016 (interrupted transaction) | Refused everywhere; no remedy but `gov recover` | Not refused |
| High, subject-scoped | Not refused (proposing relies on nothing); on the block's subjects it is the remedy | Not refused |

**Change.**
- `handoff.create` joins `WORK_REMEDIES`, `ALL_REMEDIES` and `DECLARED_REMEDY_OPS`.
- `handoffs::create` now uses `guard_write_host` plus `scheduler::admit`, with its subjects (the task record, the inputs its manifest delivers, the task's work subjects) and the task's declared `remedies`. Before, the generic subject-less guard refused every handoff under a global block, including the remediation's.
- A remedy admission is reported (`availability`).

**Tests.** Lib `scheduler::tests::proposals_and_handoffs_are_refused_by_what_they_rely_on_and_admitted_when_they_remedy`. Certification `r4_residual::the_remediation_handoff_stays_available_under_the_block_it_repairs`: a secret in `src/`; the generated security remediation is handed off as the block's remedy; unrelated work is refused `HEALTH_HARD_BLOCK`.

**IP-R3-WS04-09 docs** (`docs/ARCHITECTURE.md`, `docs/COMMANDS.md`):
- system propagation transactions (`origin: system`), and `origin` / `record_seal` in `gov cit list`;
- `t2_binding` in `gov artefact show`;
- `EXPERIMENT_NOT_PROMOTED` at approve and at execute;
- `EVIDENCE_NOT_GOVERNED`, `INHERITED_INPUT_UNSATISFIED` and `NO_IMPLEMENTATION_PRODUCED`;
- CIT-E relationship-integrity verification;
- the snapshot locations and the OS re-seal rule;
- plus this round's changes: registration through its transaction, rebuild-time propagation, the move at update, the binding status and hard-block scoping.

---

## 4. Existing tests changed, and why

No test was renamed, removed, skipped or weakened. `evidence/identity-and-scope.out` shows no test name missing at the final commit.

| Test | Change | Reason |
|---|---|---|
| `ws07::register_approved` (shared helper, used by arch, repair, repair2, repair3, ws03_r3, ws06, ws07, ws08_r3) | Answers the execution gate and the gate of the registration's change transaction, then registers. It still asserts `registration_gate` is the execution gate, and asserts the transaction COMMITTED | INT3-O1: the registration is written only by its change transaction |
| `ws07::a_registration_is_approved_only_by_a_gate_raised_for_exactly_it` | After answering g2, asserts the registration stays **unwritten** until the change gate (≠ g2) is answered, then registered with the transaction COMMITTED | INT3-O1 (strengthened: neither answer stands in for the other) |
| `ws07::declared_model_and_runtime_artefacts_are_part_of_what_the_owner_approves`, `repair3::plugin_descriptors_can_never_authorise_themselves` (p-elev), `repair2::plugins_are_governed_capabilities_not_arbitrary_commands` (netembed) | Their own two-step sequences also answer `change_transaction.human_gate` | INT3-O1 |
| `repair3::plugin_descriptors_can_never_authorise_themselves` | The execution marker is cleared right after the L4 registration, before the L0/L1 no-execution assertions | CIT-E refreshes the index under the registering L4 role once the owner approved execution (K2), which may run that approved plugin; the test measures whether L0/L1 can execute it |
| `ws04r3::direct_propagation_is_a_sealed_system_transaction_that_covers_its_marks` | The dry run is taken before the rebuild; the rebuild reports `upstream_changes.propagated`, and every property is asserted on the transaction the rebuild records; the next claim finds nothing | INT3-O2 (the integration had moved it to the claim for the same reason). The claim-time path stays covered by `ws05r3` |
| `ws05r3::stale_inputs_are_seen_propagated_at_claim_and_cleared_only_by_retest_evidence` | The rebuild moved after the claim (the DAG, list and claim read records, not the index) | Keeps observing the claim-time propagation this test is named for (INT3-O2) |
| `ws04r2::upstream_change_reaches_completed_work` | After a direct change and a rebuild, the change is detected **and propagated** by the rebuild; `cit propagate` finds nothing left | INT3-O2 |
| `ws08_r3::t2_facts_…` | `!contains("0 record(s) not honoured")` became `!contains("; 0 record(s) not honoured")` | Machine A's registration now also carries its transaction and gate, so C discloses 20 records, and "20 record(s)" contains "0 record(s)". The property (C discloses what it does not honour) is unchanged |
| lib `adopt::tests::command_test_permissions_come_from_policy_and_the_designated_duty` | The A7 verifier's basis is `TOOL_PERMISSIONS.roles.migration-verifier` from the template; the reviewer holds no RUN_TESTS; the designated-duty fallback is asserted with a policy that does not list the verifier | IP-R3-WS09-4 |
| `migration::command_tests_execute_only_governed_commands_for_permitted_roles` | A7's report records the authorisation by `TOOL_PERMISSIONS.roles.migration-verifier` | IP-R3-WS09-4 |
| lib `verification::reporting::tests::a_coverage_gap_is_confirmed_unless_every_line_is_held_with_its_heading_markers` | **Replaced under its name** (§3.4) | IP-R3-WS02-10 with IP-R3-WS06-4 |

**New tests (12)**

| Test | What it proves |
|---|---|
| cert `r4_residual::a_plugin_registered_inside_a_claimed_task_closes_on_its_os_proposed_change_transaction` | INT3-O1: K3 (auto-proposed, simulated, governance and security) and F4 (separate execution gate) both hold; the close accepts the registration on CIT-E's writes; bound to content |
| cert `r4_residual::a_registration_change_approved_without_its_execution_approval_writes_nothing` | INT3-O1, F4 direction: CIT-E refuses `PLUGIN_NOT_APPROVED` and rolls back; a new transaction after the execution approval; in-force repeat `unchanged` |
| cert `r4_residual::a_direct_upstream_change_observed_at_an_index_rebuild_is_propagated_there_once` | INT3-O2: rebuild-time propagation, deferred under FREEZE_WRITES, idempotent, the same through `memory rebuild` |
| cert `r4_residual::the_t2_binding_status_is_reported_and_machine_scope_sealing_on_a_provisioned_machine_is_disclosed` | IP-R3-WS03-6, IP-R3-WS08-3, IP-R3-WS03-8 |
| lib `verification::reporting::tests::binding_status_findings_raise_an_unhonoured_authority_and_disclose_machine_scope` | The medium cases (authority not honoured; bound but not the active key), the low disclosure, nothing on an unprovisioned machine, and FOREIGN on a bound machine |
| cert `r4_residual::a_repository_contract_rule_that_never_decides_is_reported` | IP-R3-WS06-4 |
| cert `r4_residual::skill_bindings_are_written_where_they_belong_and_a_legacy_file_moves_on_the_next_write` | IP-R3-WS06-7 |
| cert `r4_residual::an_update_moves_the_tracked_os_stores_and_a_rollback_restores_the_previous_layout` | IP-W7R3-5 and IP-R3-WS06-7 at upgrade; rollback restores the layout |
| lib `migrations::framework::tests::relocate_os_stores_moves_tracked_stores_bytes_unchanged_and_only_them` | The migration op: dry run, move, idempotence, machine-local store refused |
| cert `r4_residual::declared_model_and_runtime_artefacts_are_part_of_the_retrieval_profile_identity` | IP-W7R3-6 |
| lib `scheduler::tests::proposals_and_handoffs_are_refused_by_what_they_rely_on_and_admitted_when_they_remedy` | IP-R3-WS04-11 semantics |
| cert `r4_residual::the_remediation_handoff_stays_available_under_the_block_it_repairs` | IP-R3-WS04-11 end to end (availability rule) |

---

## 5. Optional items

| Item | Status | Reason |
|---|---|---|
| IP-W7R3-10 (dev-profile `sha2`) | **done** | `[profile.dev.package.sha2] opt-level = 3`; the release profile is unchanged. The debug certification suite runs registrations through CIT-E now (§1), so debug hashing speed matters |
| IP-R3-WS03-8 (`gov status` scope) | **done** | `gov status` → `t2_sealing {scope, bound, portable, reason}` |
| INT3-O3 (floors digest via an `srr::state` helper) | **not done** | The read is a digest read, not a writer; the AR-0033 census `floor_lower_or_reset` is 4/1/0/**0**. Making WS-8's grep exact means adding a function to `runtime/src/srr/state.rs`, an R1-listed §6 file whose unchanged state WS-8's own invariant script pins. That is not "cheap and safe" |
| IP-R3-WS04-03 (producer-rule filters) | **not done** | A refactor of the DAG, receipt and `continue` filters; no functional gain |
| IP-R3-WS04-06 (`current_stale_links` removal) | **not done** | Removing it would delete WS-2's unit test `a_completed_change_transaction_is_not_a_stale_link_to_what_it_changed`; the handoff forbids removing tests |
| IP-R3-WS02-11 (CIT-E refuse at entry) | **not done** | The same outcome more cheaply, but it changes what a refused non-remedial execution reports (no rollback details); not needed |

---

## 6. Availability rule on what I touched (P2-HO-0031)

- **Registration.** It now passes G0 through its transaction (`cit.propose`/`approve`/`execute` with the plugin's paths). A block refuses it only where its scope reaches, or globally for a critical block (BC-P2-06: a hard-block state refuses a CIT proposal). Refusals are typed (`HEALTH_HARD_BLOCK`), and FREEZE/PAUSE refuse it as before.
- **Rebuild-time propagation.** The rebuild stays available under every control; the propagation is deferred and reported, never forced.
- **Handoffs.** The remediation handoff is a remedy; unrelated handoffs are refused only under a global block.
- **New findings.** They are medium (authority not honoured) or low (machine-scope sealing, shadowed rule, D033 disclosures). None hard-blocks (hard-blocks are ≥ high).
- No refusal a repair-delta class requires was reopened.
- **G0.** No new subcommand was added. Every changed path runs under existing labels (`plugins register`, `rebuild-memory`, `memory rebuild`, `handoff create`, `update --apply|--rollback`, `health skills --record`). The internal write guards use existing labels (`cit propose|approve|execute|propagate`). `ws03::every_cli_command_label_is_classified_by_g0` passes.

## 7. Remaining integration points and observations (for the verifier, the integrator and round-5 routing)

| Id | For | What |
|---|---|---|
| R4-IP-1 | verifiers and probe authors | Any probe that registers an executable plugin by answering only the first gate must also answer `change_transaction.human_gate` (INT3-O1). Labelled derived copies are given for WS-7's IP probe and named checks. Others that register plugins (e.g. gamma-r F4, synthesis LEAD-X4, WS-3's R3 probes, WS-2's supplementary) will show the registration pending unedited |
| R4-IP-2 | WS-1 evidence map (P2-AR-0042 or its successor) | Owners for the new tests (§4 table): K3/F4/BC-P2-13 in-task → the two INT3-O1 tests; W6/G1 → the INT3-O2 test; BC-P2-31 → skill-bindings and update-relocation tests; S6/P2-ADJ-0002 observability → the binding-status tests; L4/O5 availability → the handoff tests; D4/D5 → the profile-identity test; B1/path map → the shadowed-rule test |
| R4-O1 | routing (WS-7/WS-5) | `gov tools install` inside a claimed task writes `governance/project/tools/<id>.yaml`, the same class of material governance change as a plugin descriptor. Its close would be refused `MATERIAL_CHANGE_REQUIRES_CIT`, as INT3-O1 was. The same mechanism applies unchanged (the installation proposes its change transaction; CIT-E writes the tool descriptor). Not routed this round, not changed |
| R4-O2 | routing / verifier | `gov plugins unregister` still writes the sealed registry directly, not through a change transaction. It is the fail-safe direction, and the registry is OS-managed and sealed, so a close accepts it. Whether K3 wants impact simulation for de-registration is not stated by the sources I read |
| R4-O3 | WS-8 (probe maintenance) | WS-8's `r1-invariants.sh` line "floors_path( outside state.rs = 1" stays at 1 (INT3-O3 not done, §5) |

Also carried from integration-3, not routed and not reopened: INT3-O4 and R3-WS5-11.

## 8. Owner-decision questions

None. The one design choice with a user-visible cost is two approvals per plugin registration (§1.1). The handoff states that neither requirement is an owner question, and its own example is two approvals that reference each other.

## 9. Files changed (base `cae2f67` → `34e3725`)

**Runtime:**
- `capabilities/governance.rs`
- `cit/mod.rs`, `cit/materiality.rs`
- `memory/indexer.rs`, `memory/profile.rs`, `memory/benchmark.rs`
- `migrations/framework.rs`
- `orchestration/handoffs.rs`, `orchestration/control.rs` (comment)
- `paths.rs`
- `scheduler/catalogue.rs`, `scheduler/mod.rs`
- `skills.rs`
- `status.rs`
- `update.rs`
- `verification/currency.rs`, `verification/mod.rs`, `verification/reporting.rs`
- `doctor.rs`
- `adopt.rs` (unit test)

**CLI:** `cli/src/main.rs` (two `IndexOptions` flags and a help comment; no new subcommand).

**Framework:**
- `KERNEL.yaml` (`cit` 1.2.0, `migration` 1.3.0)
- `schemas/cit.schema.json`, `schemas/migration.schema.json`
- `overlay-templates/TOOL_PERMISSIONS.yaml`, `overlay-templates/REPOSITORY_CONTRACT.yaml` (comment)
- `policies/AUTHORITY_POLICY.yaml` (comment)

**Other:**
- `migrations/M-4.1.5-4.1.6.yaml`
- `capabilities/PROTOCOL.md`
- `docs/ARCHITECTURE.md`, `docs/COMMANDS.md`
- `Cargo.toml` (dev profile)

**Tests:**
- `tests/certification/r4_residual.rs` (new), `main.rs` (`mod` line)
- `ws07.rs`, `repair2.rs`, `repair3.rs`, `ws04r2.rs`, `ws04r3.rs`, `ws05r3.rs`, `ws08_r3.rs`, `migration.rs`

**Not touched:**
- WS-1's round-4 files: `runtime/src/contracts.rs`, `framework/contracts/**`, the acceptance schema, `tests/governance/capability-evidence-map.yaml`, `docs/generated/**`;
- `release/verification/`, `release/root-of-trust/`, `release/releases/`, `release/orchestration/phase-1/`, `release/capability-baseline/audit-0/`, other workstreams' `repair-1/` directories;
- Contract v3 (`4c2df291…5ed3`).

See `evidence/identity-and-scope.out`.

## 10. Evidence index (`evidence/`)

| Path | What |
|---|---|
| `identity-and-scope.out` | Digests (base, final), release `gov`, commits, files changed, protected-path, WS-1 and other-workstream scope checks, Contract v3 and frozen-contract sha256, tests renamed or removed (none) and added |
| `regression/` | lib, certification chunks, summary and union check, chunk runner, release build, warnings, Python plugin tests, rustfmt. `superseded/` holds earlier runs: the certification chunk that caught the §6 regression (§1.4), and the `ws04r2` failure fixed in `34e3725` |
| `r1-heldout/` | Phased runner (a copy of integration-3's; changes listed in its header), S1 labelled copy, run output (byte identity, per-suite summary, census, S1, S2), `failure_messages.py`, `failure-messages-vs-integration-3.txt` |
| `int3-o1/` | WS-7's IP probe (unedited and labelled derived) and WS-7's named checks (unedited and labelled derived), runner `run-int3-o1-probes.sh`; `superseded/` holds pre-final runs |
| `audit-probes/` | Runners (copies of integration-3's), `final/`: zeta-r W12 (unedited and the integration's `g1-claim` derived copy), alpha-r A5 (unedited and WS-3's labelled copy); `superseded/` holds runs at earlier binaries |

## 11. Process disclosures

- Model: Claude Opus 5 (1M context), `claude-opus-5[1m]`. Fresh context. No sub-agents were used, and the owner was not contacted. I read no session or agent transcript, no task-output store and no user auto-memory.
- One test run exceeded the tool's 10-minute foreground limit and was moved to the background by the harness. Its output went to my own file (via an in-command redirect), which I read; the task-output store was not read. After that, every long run was split into foreground chunks.
- `rm` is denied in this environment and was not used. Superseded outputs were moved into `superseded/` directories, and my own scratch trees stay under `target/P2-AR-0043/`.
- The first attempt at running WS-3's derived A5 copy used a path expanded after a `cd` and could not open the file. It was moved to `audit-probes/superseded/` and rerun correctly.
- The derived-probe runner copy prints a header line that still reads "P2-AR-0041", because its only change is the scratch variable (stated in its header). The recorded HEAD and binary identify the tree.
- The machine was shared with a parallel builder (P2-AR-0042) during the runs. Timings are indicative only.
