# P2-AR-0041 — Repair iteration 1, round 3: integration report

| Field | Value |
|---|---|
| Run | P2-AR-0041, a fresh `capability-repair` **integration builder**. Model: Claude Opus 5 (1M context), `claude-opus-5[1m]` |
| Handoffs | P2-HO-0040 (round-3 integration). Method from P2-HO-0019 and P2-HO-0030. Rules from P2-HO-0031, P2-HO-0020 and P2-HO-0010. Adjudications P2-ADJ-0002 and P2-ADJ-0003. Each round-3 builder's `repair-1/r3-<ws>/00-REPAIR-REPORT.md` |
| Branch / base | `phase2/repair-1-r3-integration`, from `a53d15b6cef813bc474f03aa8ca39cbfcc6e0b57`. Its product code equals the round-3 base `53897c1` (`product_code_digest 797da37c…1fe1`) |
| Merged | `phase2/repair-1-r3-ws03` `7d0e0e0`, `-ws08` `a88d268`, `-ws05` `0403458`, `-ws04` `6094199`, `-ws02` `65c3bd7`, `-ws06` `3694df8`, `-ws07` `d3809db`, `-ws09-11` `2ec4656`. All eight start from `53897c1`. They were merged in that order with `--no-ff`. The merges-only tip is `8972c16` |
| Integrated product tip | **`e3b6cfbcaefafa4f538f604be52dcde41c581e85`**. `product_code_digest 1d3e9f590ad63c7e16b63662652959fea76773ff642c1fe57705cbe929785df7`. `governed_state_digest 2514b9fb46b140351f2898fbd99965a99cff4f19823c667c5affa200373235be`. `e3b6cfb` adds one certification test to `22d43ce`, whose product digest is `2dca81ff…0c940`. `runtime/`, `cli/`, `framework/`, `migrations/`, `capabilities/`, `fixtures/` and the Cargo files are byte-identical between the two, so both build the same `gov`. The commit that adds this report and `evidence/` changes no product file and keeps both digests. |
| Verdict | **`READY_FOR_INDEPENDENT_CAPABILITY_VERIFICATION`**. The integrated tree builds with 0 warnings (release, debug and every test target). `cargo test --lib` gives 262/0 and `cargo test --test certification` gives 189/0. The Python plugin tests pass 4/4, and rustfmt is clean on every file this run touched. All four prior R1 held-out suites are at their recorded baselines, and their normalised failure messages match the round-2 integration exactly. The only exception is the known AR-0033 `hv_a::a1` size pin (census 123 files / 2304 functions, 0 violations in every §6 activity). The ONE P2-ADJ-0002 mechanism was reconciled without stopping (§3). One item is stopped with evidence: R3-WS5-11 did not reproduce (§9). |

This is an integration builder's record. It grades no repair and claims no class. Every result below is regression
evidence (Contract v3 O3). Acceptance belongs to the fresh independent verifiers.

---

## 1. Merges

All eight branches were merged with `git merge --no-ff` in the order the handoff gives. Each conflict was resolved as
the union of both sides' intent, and no other edit went into a merge commit. `evidence/merge-and-change-log.out` holds
each merge's parents and its `git show --cc`. `evidence/identity-and-scope.out` shows three things: the merges brought
in only files the eight branches changed; no protected path changed after the merges; and no other workstream's
`repair-1/` directory changed after the merges.

| Merge | Conflict | Resolution |
|---|---|---|
| `26f9a7d` ws03 | none | — |
| `020d6fd` ws08 | none (auto-merged adjacent `COMMAND_GUARDS` additions in `control.rs`) | — |
| `f656cb7` ws05 | `tests/certification/ws06.rs`: WS-3 generalised the BC-P2-31 misplaced-store assertion over `paths::OS_STORES`; WS-5 added the claims-store assertions | union: WS-3's general loop ("reported exactly while its writer keeps it in the legacy location") plus WS-5's claims assertions |
| `09cfc78` ws04 | `runtime/src/lib.rs`: WS-8 set `VERSION`/`CLI_VERSION`/`RUNTIME_VERSION` to 4.1.6; WS-4 set `INDEX_VERSION` to `4.1.5-idx5` | both |
| `7726854` ws02 | none | — |
| `e26dd1b` ws06 | `tests/certification/main.rs` (`mod` lines) | both |
| `73ac04b` ws07 | `tests/certification/ws06.rs`: WS-7's registry-location assertions against the same block | the general loop (HEAD) plus WS-7's registry assertions |
| `8972c16` ws09-11 | none | — |

Straight after the merges (`8972c16`): lib 260/1 (the kernel's schema-version drift check) and certification 166/17
with 1 ignored (`evidence/regression/*.after-merges-8972c16.out`). Everything below was addressed by the integration
commits in §2.

## 2. Every change beyond the merges

Eight product commits and one test commit follow the merges. Each is described in its commit message, and each is
listed here with its reason.

| Commit | Files | Change | Why |
|---|---|---|---|
| `0b80c87` | `runtime/src/project.rs` | `Project::invalidate` also resets the schema registry | WS-9's `sync_overlay_template` delivers WS-6's new `REPOSITORY_CONTRACT` (class `operational`, mutation `os-only`, schema 1.1.0). The overlay was validated against the *previous* kernel's schemas, so every update failed `OVERLAY_INVALID` |
| | `framework/KERNEL.yaml` | `schema_versions` mirror every round-3 bump: adoption-baseline 1.2.0 and migration 1.2.0 (WS-9); cit 1.1.0 and record 1.1.0 (WS-4); index-manifest 1.2.0 and repository-contract 1.1.0 (WS-6); plugin-descriptor 1.4.0 (WS-7); task 1.2.0 and test-obligation 1.1.0 (WS-5). `health` joins `payload_dirs` | IP-R3-WS08-7 (release build and tests refuse drift). R3-WS5-9. IP-R3-WS08-5: WS-2 removed the planted literal, and the kernel's own scanner finds `framework/health` clean (enforced by `ws08_r3`) |
| | `tests/certification/ws04r3.rs` | direct-propagation test: task class `discovery` → `refactor` | The work writes `src/**`, and WS-5's BC-P2-13 in-task hook refuses a discovery task that changes product source (WS-5 made the same change in ws04r2). Assertions unchanged |
| `fcb049e` | `runtime/src/srr/binding.rs`, `runtime/src/t2.rs`, `runtime/src/srr/mod.rs`, `cli/src/main.rs`, `runtime/src/orchestration/control.rs`, `framework/policies/AUTHORITY_POLICY.yaml`, `tests/certification/ws03_r3.rs` | **ONE P2-ADJ-0002 mechanism** (§3) | handoff: required reconciliation |
| `77157f1` | `runtime/src/cit/binding.rs`, `runtime/src/doctor.rs`, `runtime/src/verification/reporting.rs` | `cit::binding::binding_of` carries the underlying T2 binding. New `sealed_elsewhere()` (FOREIGN / UNAUTHORISED / KEY_UNAVAILABLE). D033 and `os_binding_integrity` disclose CIT state sealed on another machine and do not fail or grade it high. Modified, hand-written or copied state in force stays high | WS-2 × P2-ADJ-0002: WS-2's new D033/CIT rows treated any non-verified CIT state as tampering. WS-8's two-machine test (anchor-only machine C must *disclose* the owner's records it does not honour) found it |
| `8b3fd14` | `tests/certification/ws04r3.rs` | direct-propagation test observes the propagation that the next `task claim` runs. It asserts every property of the system transaction the claim records | WS-4 × WS-5: WS-5 wired WS-4 R2-3 (`detect_and_propagate` at claim), so the test's premise (a change propagated after another task's claim) can no longer arise through `gov`. §6 |
| `5f86937` | `runtime/src/t2.rs`, `tests/certification/ws04r3.rs` | `cit` joins `t2::SEALED_RECORD_TYPES`. `ws04r3::a_cit_declined_during_another_tasks_claim_does_not_block_its_close` un-ignored; its src-writing task class becomes `refactor` | IP-R3-WS04-01, in the routed order. Step 1 (re-seal in `gates::answer`/`revoke`) was already in WS-3's round-3 `gates.rs` as `t2::seal_if_verified`, which is equivalent to WS-4's 6-line patch; the patch no longer applies textually |
| `68f2e4a` | `runtime/src/orchestration/{tasks,dag,readiness,generation}.rs`, `runtime/src/verification/lineage.rs`, `runtime/src/migrations/references.rs`, `runtime/src/t2.rs`, `tests/certification/{integration_r3,main}.rs` | Task records are sealed on every OS write (a created record is sealed; a rewritten one is re-sealed only if it verified before), and `task` becomes a sealed kind. The claim baseline records the task/CIT records already unsealed at claim (`LEGACY_SEALED_KINDS`), and a close reports rather than refuses a `gov` rewrite of one of them. `OS_MANAGED_PREFIXES` gains `governance/registry/`. Adoption treats OS-generated work (verifying seal plus OS-owned provenance, `generation::is_os_generated`) like event records, not dependants | WS-5 r2 IP-R3-1 final step, ordered after the WS-3/WS-4 re-sealing. R3-WS5-8. IP-W7R3-1 (required). The brownfield regression: WS-2's new `legacy_authority` finding made WS-5 generate a remediation task naming the legacy file, which changed the destructive gate's subject hash and voided the owner's answer |
| `f1cb985` | `runtime/src/scheduler/{mod,catalogue}.rs`, `runtime/src/orchestration/{control,tasks}.rs`, `runtime/src/update.rs`, `runtime/src/cit/mod.rs`, `runtime/src/lifecycle/mod.rs`, `framework/policies/AUTHORITY_POLICY.yaml` | **One availability host API** (§4). `cit propose` leaves `GOVERNED_WORK_OPS`. `cit::guard_paths` keeps file targets. `with_record_aliases` never adds an empty alias (new unit test). `record_research_evidence: L1` plus `lifecycle::RECORD_AUTHORITY` plus the 12 research/experiment/data labels | handoff WS-2 items IP-R3-WS02-01/-02/-03/-04; IP-R3-WS08-4; IP-R3-WS03-4. The empty-alias defect: a record that does not parse loads with an empty id, and its empty alias glob-matched every path. WS-8's entry-guard test found it after the convergence |
| `22d43ce` | `runtime/src/memory/integrity.rs`, `runtime/src/recovery.rs`, `runtime/src/verification/mod.rs`, `runtime/src/release.rs`, `cli/src/main.rs`, `migrations/M-4.1.5-4.1.6.yaml`, `tests/certification/{common,ws03_r3,integration_r3}.rs`, docs | TESTS work→work admitted (narrowly). The recovery report writes string items and is sealed. `misplaced_os_state` becomes medium. `gov release record` is wired. CLI `task show` → `tasks::show`. The post-command generation is skipped after every guard refusal. `tree_hash` excludes `.governance-state/**`. The migration description is updated. The ws03_r3 gate test strips a seal explicitly. Docs | IP-R3-WS02-07 (proved by `integration_r3::a_cit_invalidating_done_work_leaves_graph_integrity_and_d015_clean`); R3-WS5-7 = IP-R3-WS02-08 (+ IP-R3-WS04-04); IP-R3-WS02-09; IP-R3-WS03-5 / IP-R3-WS08-8 / IP-R3-WS04-07; R3-WS5-4; R3-WS5-1; IP-R3-WS09-3; IP-R3-WS08-6; IP-R3-WS08-2 |
| `e3b6cfb` | `tests/certification/integration_r3.rs` | new test `a_readiness_regression_made_through_change_control_is_refused_at_close_by_g2` | WS-2's G2 readiness duty at close in the union (§6, §7.4). Test only |

No commit touches Contract v3, `release/verification/`, `release/root-of-trust/`, `release/releases/`,
`release/orchestration/phase-1/`, `release/capability-baseline/audit-0/` or another workstream's `repair-1/`
directory. rustfmt (edition 2021) `--check` is clean on every Rust file changed after the merges. The two `rc=1` lines
in `evidence/regression/rustfmt-check.out` are hunks in child modules that rustfmt follows from `srr/mod.rs` and
`tests/certification/main.rs` (`srr/breakglass.rs`, `srr/metadata.rs`, `section6.rs`, `srr.rs`). None of those four
files is changed by this integration, and they are left as they are.

## 3. P2-ADJ-0002: one mechanism

**Shape.** There is one delegated role, one authority document format, one provisioning command and one keyring API,
all in `runtime/src/srr/binding.rs`. `runtime/src/t2.rs` seals and verifies only through them.

| Element | The one kept | Taken from | Removed |
|---|---|---|---|
| delegated role | `t2-binding` in the provisioned root (`srr::binding::ROLE`, re-exported as `t2::AUTHORITY_ROLE`) | both (identical) | — |
| authority document | WS-8's `t2-binding-authority`: authority id, **version** (never lowered on a machine; a conflicting document with the same version is refused), expiry, optional **machine list**, keys by **key id + SHA-256 commitment** with exactly one `active` and any number of `retired`. Signed at the role's threshold; `gov` only verifies | WS-8 | WS-3's `t2-binding-provisioning` bundle, per-key `authorities/<id>/` store, `AUTHORITY_ID_PREFIX`, and its second document verifier (`provision_authority`) |
| provisioning command | `gov trust bind --authority <doc> --key <file>` (machine-trust domain, administrator). Refused below floor (break-glass guard, `SRR_BELOW_FLOOR_REFUSED`), from repository content (both WS-8's source check and WS-3's enclosing-governed-project check), via the environment, on an unprovisioned machine, under a root that does not delegate the role, below threshold or by another signer, expired, older or conflicting, for an unlisted machine, and for a key the document does not authorise by id and commitment | WS-8 (+ WS-3's repository check) | `gov trust t2-binding --provision` |
| keyring API | `srr::binding::keyring()` / `keyring_at()` / `held_keys()`: the authority is re-verified **at use** against the current trusted root (signature, threshold, delegation, expiry, the recorded document) and must list this machine; keys held at `<state>/t2-binding/keyring/<key_id>.json` (0600, dir 0700) | WS-8, plus the machine list checked at use as well as at bind | `srr::binding::status()` (one status: `t2::binding_status()`, surfaced by `gov trust status` → `t2_binding`) |
| portable seal | `hmac-sha256/t2-v2` over authority id, **key id**, sealing machine id, operation, time and content | WS-3's v2 seal, which binds authority/machine/operation/time/content, extended with the key id so rotation is unambiguous | — |
| continuity | `gov trust reseal [--dry-run]` (`reseal_t2_bindings`, L4; `--dry-run` Read): re-seals under the active key what this machine sealed with its own key **while provisioned**, keeping the recorded operation and time. Nothing sealed while unprovisioned is re-sealed, and neither is anything whose seal does not verify | WS-3 | `gov trust t2-binding --reseal` |
| machine key | `<state>/t2-binding/key.json` is never replaced or destroyed by binding. It keeps working unbound, and seals stay in the machine scope | WS-3 (WS-8 installed the binding key over the machine key) | — |

**Rotation and revocation: the stronger of the two.** WS-8's per-key semantics are kept. `retired` keys stay honoured
for seals made before a rotation, and a key absent from the current version is revoked (`UNAUTHORISED`). Versions are
monotonic (`T2_BINDING_AUTHORITY_ROLLBACK`), and a conflicting document with the same version is refused
(`…_CONFLICT`). The optional machine list authorises machines individually. WS-3's mechanism had no per-key
revocation: an authority stopped being honoured only when root succession dropped its signer, and the latest-issued of
several held authorities sealed. Both builders re-verified the authority at use against the current root, and that is
kept. **The one semantic difference was expiry.** For WS-3, expiry bounded only when an authority may *seal*, and
records sealed while it was valid stayed honoured. WS-8's keyring refuses an expired authority at use. The kept rule is
WS-8's, because it is the stronger revocation rule: it bounds how long a leaked binding key stays useful. After expiry,
none of the authority's seals is honoured (UNAUTHORISED, and new seals fall back to the machine scope) until the
administrator binds a renewed version. That restores everything, because a renewed document that lists the same keys
re-honours every record sealed under them. No WS-3 test asserted honouring after expiry: its tests assert install-time
expiry refusal and sealing selection, both kept. Root succession that drops the delegation, and alteration, likewise
stop every seal of the authority being honoured. Because `t2.rs` caches
the machine's view keyed by a state fingerprint (WS-3's cache, keyed by the provisioning record, not the trust-anchor
path), the view re-checks expiry against the current time at every use. The machine list is also enforced at use
(`T2_BINDING_MACHINE_NOT_AUTHORISED`), not only at bind. WS-8's rule that **a bound machine honours only owner facts**
is kept: its own machine-scope seals are `UNAUTHORISED` (with a `gov trust reseal` hint) until they are re-sealed.

**Why this shape, not a new design.** Both builders implemented the same determined requirement with the same trust
root, role and "commitments only, no signing inside `gov`" (SRR-R0-L4). WS-8's document, command and keyring already
had the richer lifecycle (versioning, active/retired, machine list, rollback and conflict refusals) and carried the
two-machine harness every round-3 test runs on. WS-3's seal format and reseal continuity were the only parts WS-8 did
not have. The one point where they disagreed (expiry at use, above) is a revocation-semantics question, and the handoff
settles it: rotation/revocation from the stronger of the two. No trade-off the sources leave open had to be chosen,
and nothing was stopped.

**Every property either builder's tests assert is kept.** WS-8's `ws08_r3` tests are unchanged and pass. WS-3's
`ws03_r3` tests keep their names and assertions and moved onto the one harness (suite root plus suite owner's
authority, `clone_to_machine`, `foreign_owner`). The seal is still re-derived independently from its documentation.
Only the typed codes follow the kept command: `T2_AUTHORITY_UNPROVISIONED` → `T2_BINDING_UNPROVISIONED`;
`…FROM_REPOSITORY_REFUSED` → `T2_BINDING_FROM_REPOSITORY_REFUSED`; `…ROLE_NOT_DELEGATED` → `T2_BINDING_NOT_DELEGATED`;
`…KEY_MISMATCH` → `T2_BINDING_KEY_NOT_AUTHORISED`; `…EXPIRED` → `T2_BINDING_AUTHORITY_EXPIRED`; `…INVALID` →
`T2_BINDING_AUTHORITY_INVALID`; a wrong signer or another owner's root → the root verifier's `SRR_THRESHOLD_NOT_MET`.
WS-3's four `t2.rs` unit tests are kept, with two renamed to the unified terms: WS-3's "latest issued" authority
selection is now "the one accepted authority, never older" (a rollback is refused at bind). WS-3's own probe, run as a
labelled derived copy on the unified command, gives **26/26**, the same as its own record. The unedited run fails only
on the removed `trust t2-binding` surface (§7.3).

## 4. One availability host API (WS-2 × WS-5 × WS-8)

Every host uses WS-2's scheduler API (`Request`, `admit`, `confirm_remedy`, `guard`, `subjects_reach`; catalogue
`BlockRule{min_severity, operations, scope, remedies}`).

- **Task create and claim** (`tasks::guard_work`) call `control::guard_write_host` (kernel trust, break-glass, emergency
  controls) and then `scheduler::admit` with the task's subjects: id, record path, declared inputs, feature,
  dependencies and allowed paths (`verification::close_subjects`; IP-R3-WS02-03). A subject-scoped block therefore
  leaves independent claims available at the host as well as in the decision. The admission is returned as
  `availability`.
- **WS-5's "work that remedies a block stays available"** is expressed in WS-2's catalogue. `task.create` and
  `task.claim` join `WORK_REMEDIES`/`ALL_REMEDIES` as `DECLARED_REMEDY_OPS`. They are admitted as a block's remedy only
  when the work declares the block's check (the task's `remedies`) **and** its subjects reach the block's subjects.
  This is the conjunction of both builders' conditions. WS-2's own guard documentation names "creating, claiming … the
  repairing task" as allowed non-committing remedies.
- **Update** (IP-R3-WS02-02 / IP-R3-WS08-4): `entry_guard` = `scheduler::admit(UPDATE_APPLY, UPDATE_SUBJECTS)`, applied
  after `authority::require`. A non-remediable block refuses at entry, typed, with its rule. `scheduler::confirm_remedy`
  runs before commit, and `HEALTH_REMEDY_INCOMPLETE` rolls the transaction back. `update_can_remedy` is now the
  catalogue's declaration. WS-8's parallel partition (`UPDATE_REPLACES`) is removed.
- **CIT**: `cit propose` leaves `GOVERNED_WORK_OPS` (IP-R3-WS02-01), because its host guards it with its paths, and
  `guard_paths` keeps file targets (IP-R3-WS02-04). WS-2's AV.2b-e2e goes FAIL → PASS (§7.3).
- **Work generation** (review, R3-WS5-1/-2): the post-command hook runs only after a Write-class project command. It
  is skipped after every refusal of the guard (`G0_UNCLASSIFIED`, `AUTHORITY_DENIED`, `FROZEN`, `PAUSED`, `USAGE`,
  `ROLE_UNDECLARED`, `HEALTH_HARD_BLOCK`, `KERNEL_TAMPERED`, `KERNEL_UNANCHORED`, both below-floor refusals).
  `reconcile` itself passes `guard_write("work generation")`, so nothing is generated under FREEZE/PAUSE or on an
  untrusted kernel. `generation::create_generated` writes task records without an availability admission. That was
  reviewed and kept, because creating a record relies on nothing: the availability rule decides when the generated
  work is *claimed*. `task generate` is Write (`replan_tasks`, L2) and `--dry-run` is Read. `evidence/g0` measures both
  under freeze and pause (§7.5).

## 5. Status of every routed item

| Item | Status |
|---|---|
| P2-ADJ-0002 one mechanism | done (§3) |
| IP-W7R3-1 `governance/registry/` in `OS_MANAGED_PREFIXES` (required) | done (`68f2e4a`). WS-7's probe: the registry is no longer undeclared or out of scope at close. The close now stops on the plugin **descriptor** instead (WS-5's materiality; §8 INT3-O1) |
| IP-R3-WS04-01, in order: gates re-seal → `cit` sealed kind → un-ignore | done (`5f86937`). Step 1 was already present in WS-3's `gates.rs`. The test is un-ignored and passes |
| WS-5 task-record sealing (ordered after WS-3/WS-4 re-sealing) | done (`68f2e4a`), proven by `integration_r3::task_records_are_sealed_and_os_writes_inside_another_claim_window_are_honoured`, `…a_task_record_written_outside_gov_inside_a_claim_window_is_refused_at_close`, `…a_legacy_unsealed_task_rewritten_by_gov_inside_a_claim_window_is_reported_not_refused` |
| R3-WS5-1 / -2 / -3 (generation hook, guards, module) | reviewed; hook skip list completed (`22d43ce`); classes measured (§4, §7.5) |
| R3-WS5-4 `task show` | done (`22d43ce`) |
| R3-WS5-5 claims store readers | already satisfied in the union: every reader goes through `ClaimsStore::path_for` (sandbox copy WS-2 `2e72007`, currency input, D017/D026) |
| R3-WS5-6 emergency-control store | done by WS-3 (`store_path(root, "emergency-control")` + `relocate_legacy`). WS-6's relocation test passes. beta-r **D6-b2-B FAIL → PASS** (§7.4) |
| R3-WS5-7 = IP-R3-WS02-08 recovery report strings | done once (`22d43ce`) |
| R3-WS5-8 OS writes inside another claim window attributed | done by seals (CIT: `5f86937`; tasks: `68f2e4a`; `lifecycle::record_influence` already re-seals a verified record); legacy unsealed records are reported, not refused |
| R3-WS5-9 KERNEL.yaml task/test-obligation | done (`0b80c87`) |
| R3-WS5-10 cost vs Gate U SLOs | measured (§7.6). Gate U declares no latency SLO |
| R3-WS5-11 sandbox symbol route | **not reproduced**, stopped with evidence (§9) |
| IP-R3-WS02-01..-04 | done (`f1cb985`, §4) |
| IP-R3-WS02-05/-06 re-run W12-G1 and X1-G1xW6 | re-run (§7.4): X1-G1xW6 FAIL → PASS; W12-G1 as written stays FAIL; its purpose is met at the next claim |
| IP-R3-WS02-07 TESTS work→work | done (`22d43ce`) and proven |
| IP-R3-WS02-09 `misplaced_os_state` medium | done (`22d43ce`) |
| IP-R3-WS02-10 retire the heading-marker confirmation | **not retired**. The step is inert once WS-6's markers are in place, but retiring it would delete WS-2's unit test. Left to WS-2 (with IP-R3-WS06-4) |
| IP-R3-WS02-11 (optional) CIT-E refuse at entry | not done (optional) |
| P2-ADJ-0003 | respected. No H4 severity lowered. Green-baseline probes are read against the contract (§7.4) |
| IP-R3-WS03-4 research authority | done (`f1cb985`) |
| IP-R3-WS08-7 KERNEL mirroring / IP-R3-WS08-5 `health` payload | done (`0b80c87`) |
| IP-R3-WS03-5 / IP-R3-WS08-8 product-release CLI | done (`22d43ce`; all three parts present) |
| WS-6 `observe_boundaries: true` on `rebuild-memory` / `memory rebuild` | **kept**. A significant-mutation checkpoint at rebuild goes through `checkpoints::create`, which passes `guard_write("checkpoint")` and `authority::require`. Under FREEZE/PAUSE it is refused and reported, never written, and the rebuild stays allowed (FROZEN/PAUSED allow-lists). No guard or freeze property breaks |
| Template/migration convergence (IP-R3-WS06-1 / IP-R3-WS09-2) | in place: `M-4.1.5-4.1.6` delivers the `REPOSITORY_CONTRACT` template via `op: sync_overlay_template`. The schema-cache fix (`0b80c87`) made it validate |
| IP-R3-WS09-3 `tree_hash` | done (`22d43ce`) |
| Store relocations (control state, registry, claims, migration/update/CIT snapshots) | WS-6's relocation test passes. Every writer uses `paths::store_path` or its store module. The remaining literal legacy paths are legacy readers, migration code and tests (`LEGACY_REGISTRY_PATH`, `memory::claims` legacy relocation, the currency class list; see IP-W7R3-3 in §8) |
| Harness convergence | `ws03_r3` converged (§3). Every round-3 test uses WS-8's `common.rs` |

## 6. Other builders' tests changed, and why

No test was weakened, deleted or skipped. Each change states its reason in the test.

| Test | Change | Reason |
|---|---|---|
| `ws04r3::direct_propagation_is_a_sealed_system_transaction_that_covers_its_marks` | class `refactor`. It observes the claim-time propagation: a dry run shows the pending change, the claim reports `upstream_changes.propagated`, and every property is asserted on the system CIT the claim records. A later `cit propagate` finds nothing | WS-5's BC-P2-13 hook; WS-5 wired `detect_and_propagate` at claim |
| `ws04r3::a_cit_declined_during_another_tasks_claim_does_not_block_its_close` | un-ignored as the handoff requires; class `refactor` | IP-R3-WS04-01 end state; BC-P2-13 |
| `ws03_r3` (the P2-ADJ-0002 tests) | moved onto the one mechanism and harness; typed codes follow the kept command | §3 |
| `ws03_r3::gate_operations_keep_os_sealed_task_records_verifiable_and_never_bless_others` | the "unsealed task record" is now made explicitly by stripping its seal | `gov task create` now seals (task sealing) |
| `common::tree_hash` | excludes `.governance-state/**` | IP-R3-WS09-3 |
| `ws06.rs` merge blocks | union | §1 |

The integration's own tests are in `tests/certification/integration_r3.rs` (5 tests). The unit test
`scheduler::tests::a_block_about_an_unparseable_record_is_not_reached_by_every_request` is new.

**WS-2 G2 × WS-5 materiality.** WS-2's probe G2.a hand-edits the claimed task's own feature readiness. In the union,
WS-5's in-task materiality rule 10a refuses that close first (`MATERIAL_CHANGE_REQUIRES_CIT`: an implementation task
changed its feature outside change control). The close is still refused, but no test in the union reached
`TASK_READINESS_REGRESSED` end to end. `e3b6cfb` adds that proof: the regression arrives through an owner-approved CIT
inside the claim window, materiality accepts the CIT's verified write, and the close is refused
`TASK_READINESS_REGRESSED` by `verification::close_readiness`.

## 7. Regression

### 7.1 Suites (`evidence/regression/`)

| Suite | Result | Evidence |
|---|---|---|
| `cargo build --release` | 0 warnings | `cargo-build-release.out` |
| `cargo build` + `cargo test --no-run` (lib/main forced to recompile) | 0 warnings | `warnings-check.22d43ce.out` |
| `cargo test --lib` at `e3b6cfb` | **262 passed, 0 failed** (207 at the round-2 integration + 54 from the round-3 builders + 1 integration unit test) | `cargo-test-lib.e3b6cfb.out` (and `.22d43ce.out`: 262/0) |
| `cargo test --test certification` at `e3b6cfb` | **189 passed, 0 failed, 0 ignored** (136 + 48 from the round-3 builders, including the un-ignored WS-4 test, + 5 `integration_r3`) | `cargo-test-certification.e3b6cfb.out` (and `.22d43ce.out`: 188/0) |
| Python plugin tests (`capabilities/tests`) | 4 passed | `python-plugin-tests.out` |
| rustfmt `--check` on files changed after the merges | clean (see §2 for the two child-module lines) | `rustfmt-check.out` |

`export CARGO_BUILD_JOBS=2` for every build. No `GOV_*` variable was set for any suite.

### 7.2 R1 held-out suites, unedited, private path (`evidence/r1-heldout/`)

Runner: `run-r1-heldout.sh`, a copy of P2-AR-0032's with only the run id, jobs and private root changed. The four
suites are copied byte-identically (`cmp` is recorded for all 26 files) into the private, uniquely named root
`…/scratchpad/P2-AR-0041/r1-P2-AR-0041-private`. The expected checkout names (`wt/srr1-r1-verify{,-2,-3,-4}`) are
symlinks to this worktree, and the suites run against the tree's own debug `gov`. Run at `22d43ce`, which has the same
`runtime/`, `cli/` and binary as `e3b6cfb`.

| Suite | Baseline | Integrated `22d43ce` | Failing tests (identical to the baselines) |
|---|---|---|---|
| AR-0027 | 26/3 | **26/3** | heldout_srr2 b1, b2; heldout_srr3 d3 |
| AR-0029 | 26/2, `ho_f_preservation` does not compile | **26/2**, `ho_f` does not compile | ho_b b3, b6 |
| AR-0031 | 27/7 | **27/7** | hx_a a1, a5, a8; hx_b b6; hx_c c2, c3; hx_d d2 |
| AR-0033 | 30/1 | **30/1** | hv_a a1 (the size pin: 84 files / 740 functions) |

- **Census** (AR-0033 `hv_a::a1`'s own independent walk of this tree): **123 files, 2304 functions**. The round-2
  integration had 118 / 1991.
- **S1**, a labelled copy of `hv_a::a1` with only its two size assertions printed instead of asserted (byte-identical to
  P2-AR-0032's copy, so its printed label still reads P2-AR-0032): **passes**. §6 census, derived / writers / exempt /
  violations: human_gate_create 49/44/1/**0**; human_gate_approve 1/1/0/**0**; release_certification 1/1/0/**0**;
  trust_policy_mutation 8/1/0/**0**; privileged_plugin_acquisition 9/2/0/**0**; floor_lower_or_reset 4/1/0/**0**;
  present_below_floor_release_as_current 1/1/0/**0**.
- **S2**, AR-0033's `derive.py` with only its ROOT line substituted: the same census and **0 violations** in all three
  splitter configurations (indentation or brace-depth, with and without the `cfg(test)` cut).
- **Failure messages**: the normalised failure and panic messages of the unedited suites are **identical** to the
  round-2 integration's final run (42 lines each, empty diff): `failure-messages-vs-integration-2.txt`.
- human_gate_create moved from 47 derived / 42 writers at the base to 49/44. The per-builder runs show WS-3 +1, WS-4
  +2, WS-5 +2, WS-8 +1 and WS-6 −1, all with 0 violations.

### 7.3 Round-3 builders' own probes against the integrated binary (`evidence/builder-probes/COMPARE-builder-probes.out`)

| Builder / probe | Builder's record | Integrated, unedited | Integrated, labelled derived copy |
|---|---|---|---|
| WS-2 `WS02-r3-supplementary.py` | 64/65 (AV.2b-e2e FAIL) | 51/54. Groups IF1, G2 and W11 cannot claim `TASK-0001`, which is blocked by the computed scenario chain (WS-5 r3, IP-WS10-12). Every line that ran passes | **64/65** (`chain-na`: the fixture states `data_requirements_not_applicable` and the two chain cells `N/A_WITH_REASON`). AV.2b-e2e FAIL → **PASS**. G2.a PASS → FAIL: the close is refused by WS-5's materiality first (§6) |
| WS-3 `R3-WS03-probes.py` | 26/26 | 10/26. The removed `trust t2-binding` surface, plus T2C.a's pre-WS-7 registry path | **26/26** (`unified`, changes a–h in its header; the first run before change h was 25/26, kept as `…first-run-before-change-h.out`) |
| WS-4 `ws04r3_observe.rs` | 22 PASS / 0 FAIL | 19 PASS / 0 FAIL. `obs_b` panics at set-up because its `discovery` task writes `src/**` (BC-P2-13), so B1–B3 are not observed | **22 PASS / 0 FAIL** (`claim-time`: class `refactor`; B1 reads the system CIT the next claim records) |
| WS-6 `SUPP-ws06-r3.py` | 16/16 | **16/16** | — |
| WS-7 `ws07_r3_named_checks.py` | 11/11 | **11/11** | — |
| WS-7 `ip_task_close_registration.py` (IP-W7R3-1) | close refused `MUTATION_SCOPE_VIOLATION` for the registry | the registry is no longer undeclared or out of scope. The close is refused `MATERIAL_CHANGE_REQUIRES_CIT` for the descriptor `governance/project/plugins/p1.yaml` (§8 INT3-O1) | — |
| WS-8 `r1-invariants.sh` | all hold | identical except one line: `floors_path(` outside `state.rs` = 1. That is WS-2's read-only `sha_opt(&ms.floors_path(product))` in the currency fingerprint (`verification/currency.rs:460`), a digest read and not a writer. The AR-0033 census `floor_lower_or_reset` stays 4/1/0/**0** | — |
| WS-9/11 `tiny_unprovisioned_adoption.py` | 7: 5 PASS, 2 OBS | **7: 5 PASS, 2 OBS, 0 FAIL** | — |

### 7.4 Audit-of-record probes routed by the handoff (`evidence/audit-probes/COMPARE-audit-probes.out`)

- **zeta-r W12** (unedited, owner-channel root shim): identical to WS-2's record. W12-G0 ×3 PASS, W12-G1-mutation PASS,
  **W12-G1-dependency-evidence-invalidated FAIL**, and the run stops at G2 (claim of a task whose mandatory input is
  ABSENT) as before. The labelled derived copy (`g1-claim`) adds one observation. The next `task claim` of TASK-0001 runs
  `detect_and_propagate` and is refused `TASK_NOT_RUNNABLE` with "retest required after upstream change propagation
  (direct change (not through a CIT))", and `retest_required` is stored → **DERIVED-W12-G1-next-claim-propagates PASS**.
  W12-G1 as written reads `task list` straight after the incremental rebuild. Propagation is wired at claim, not at
  rebuild, so that line stays FAIL, while the stale packet is never handed out.
- **synthesis AC16-X1** (WS-5 adapter): unedited, it cannot start, because its first claim is refused by the computed
  scenario chain. The labelled derived copy (`chain-na`) gives **14/15**. **X1-G1xW6 FAIL → PASS**
  (`close_after_rebuild_ok: false`). X1-O4 FAIL: its green-before precondition does not hold, and P2-ADJ-0003 §2 rules
  that this precondition contradicts Contract v3:1136, so it is not a product defect. X1-UxO5 PASS (DEGRADED).

- **beta-r D6 rebuild guarantee** (handoff: "D6-b2-B must pass"): both builders' labelled derived copies were run
  unedited from their own evidence directories: WS-3's `D6-rebuild-guarantee.claimable.P2-AR-0034.py` and WS-5's
  `…refactor-claim.P2-AR-0036.py`, through the owner-channel root shim. Each gives **7 PASS / 1 FAIL**, where both
  builders recorded 6/2. **D6-b2-B FAIL → PASS**: the claims store (WS-5) and the emergency-control state (WS-3) both
  now live in `.governance-state/`. D6-b2-A-pin stays FAIL, as in both records: both copies drop the probe's
  hand-declared reranker, which is never registered under WS-7's plugin governance, so the line measures that
  refusal.

### 7.5 G0 behaviour of the round-3 labels (`evidence/g0/round3_labels_g0_probe.out`): **20/20**

Under FREEZE_WRITES and under PAUSE, `trust reseal`, `task generate`, `release record` and `research record` (Write)
are each refused FROZEN/PAUSED and change no tracked file. `trust reseal --dry-run` and `task generate --dry-run` (Read)
are not refused by the control. No work is generated after the refused commands. Without a declared role, every one of
the four Write labels is refused `AUTHORITY_DENIED`: there is no default role. The classification of every CLI label is
also enforced by `ws03::every_cli_command_label_is_classified_by_g0` and by the `control.rs` unit tests.

### 7.6 R3-WS5-10: generation and claim cost (`evidence/slo-cost/generation-cost.22d43ce.out`)

Release `gov` on a minimal bootstrap-installed project, 7 samples each, median (p90), in ms:

| `status` | `task list` | `task generate --dry-run` | `task create` | `task claim` | `task release` |
|---|---|---|---|---|---|
| 155 (156) | 18 (19) | 122 (123) | 419 (428) | 457 (461) | 445 (450) |

The reconciliation alone (dry run) costs about 120 ms. That is roughly what the post-command generation adds to each
governed write here, and the claim adds its G0 admission, claim-time propagation, DAG, baseline and boundary
observation. `framework/health/HEALTH_SLOS.yaml` (Gate U) declares no latency or per-write cost SLO, so the cost is
reported in absolute terms and not judged. The first run created DRAFT tasks, so its claims were refused and not
measured. It was set aside (§12).

## 8. Observations and integration points for round 4 (nothing changed for them)

- **INT3-O1 (WS-5 × WS-7, MEDIUM, not a regression of IP-W7R3-1):** a plugin registered inside a claimed task (WS-7's
  IP probe) is refused at close `MATERIAL_CHANGE_REQUIRES_CIT` for its descriptor under `governance/project/plugins/`.
  That is a governance change under WS-5's materiality, even though `gov plugins register` went through its own owner
  gate. Round 4 needs to decide whether an owner-approved registration counts as change control for its own descriptor,
  or whether registrations are expected to go through a CIT. Owners: WS-5 (materiality) and WS-7 (registration).
- **INT3-O2 (WS-2):** `W12-G1-dependency-evidence-invalidated`, as written, reads the retest flag after an incremental
  rebuild. Propagation of a direct change runs at the next claim. Either the reading is at claim (as the derived copy
  shows) or `detect_and_propagate` also runs at rebuild (IP-R3-WS02-05 allowed either).
- **INT3-O3:** WS-8's R1-invariant grep counts WS-2's read-only floors digest (§7.3). Optionally, route that read through
  a `srr::state` helper so the structural invariant stays exact.
- **INT3-O4:** legacy unsealed task/CIT records rewritten by `gov` inside a claim window are reported
  (`os_managed_unbound`), not refused. The OS never blesses them, and they stay unsealed until a governed re-issue.
- Remaining builder IPs not routed to this integration: **WS-3** IP-R3-WS03-6 (disclose machine-scope sealing on a
  provisioned machine; now via `t2::binding_status()`), -7 (PROTOCOL.md registry-portability text), -8 (optional
  `gov status` scope), -9 (alpha-r A5 control-state path). **WS-8** IP-R3-WS08-3 (D033/`os_binding_integrity` report
  the binding status; `srr::binding::status()` is now `t2::binding_status()`), -9 (probe premise for "current release"
  probes), -10 (evidence-map entries). **WS-6** IP-R3-WS06-4 (shadowed-rule finding; retire the heading-marker step
  together with IP-R3-WS02-10), -6 (evidence map), -7 (`skill-bindings.json` to `governance/registry/` + `OS_STORES`).
  **WS-9** IP-R3-WS09-4 (TOOL_PERMISSIONS for the independent roles), -5 (evidence map). **WS-7** IP-W7R3-3 (currency
  class `tools_plugins` should list `governance/registry/plugin-registry.json`; it now falls in `source`, still an
  input), -5 (relocate the registry at upgrade), -6 (memory-profile hashing and identity), -7 (`plugins registry` help
  text still names `governance/generated/…`), -9 (ARCHITECTURE registry location and template rule), -10 (optional dev
  profile for `sha2`). **WS-4** IP-R3-WS04-03 (optional producer-rule filters), -06 (optional
  `current_stale_links` removal), -09 (docs), -10 (evidence map), -11 (block scope for `cit.propose` /
  `handoff.create`, including the `handoff.create` remedy for remediation handoffs). **WS-2** IP-R3-WS02-10 (not
  retired, above), -11 (optional).

## 9. Contradictions and stopped items

- **P2-ADJ-0002: not stopped.** The two implementations reconciled without an open trade-off (§3).
- **R3-WS5-11: stopped, not reproduced.** `evidence/ws5-11/repro_retrieval_symbol_sandbox.py` runs
  `memory_retrieval_regression` with `--no-cache` so that it executes in its sandbox (`isolated_in_sandbox: true`,
  status `executed`) on a minimal project (2 symbol queries) and on the greenfield fixture (5). Both give PASS, recall@k
  1.0, MRR 1.0 and no failing query (`repro.22d43ce.out`). An earlier scratch run on an intermediate binary agreed. This
  integration did not establish which merged change, if any, removed WS-5's observation. If WS-5 still sees it, its
  reproduction (project and command) is needed.
- No contradiction with Contract v3 or an accepted boundary was found. No default role, unauthenticated answer path or
  standalone human-gate anchor was introduced, and there is no signing inside `gov`.

## 10. What I did not do

I did not grade any repair, claim any capability class, or mint a candidate. I did not retire IP-R3-WS02-10, do the
optional IP-R3-WS02-11 or IP-R3-WS04-03/-06, or do any IP not routed to this integration (§8). I did not change a
probe of record: every derived copy is a separate, labelled file.

## 11. Evidence index (`evidence/`)

| Path | What |
|---|---|
| `identity-and-scope.out` | digests of the base, merges-only, `22d43ce` and every builder tip; Contract v3 and frozen gate contract sha256; release binary; merge parents; scope checks |
| `merge-and-change-log.out` | commits, merge parents, `git show --cc` of every merge |
| `regression/` | lib / certification (after merges, `22d43ce`, `e3b6cfb`), release build, warnings, Python plugin tests, rustfmt |
| `r1-heldout/` | runner, S1 derived copy, run output (byte identity, per-suite summaries, census, S1, S2), `failure_messages.py`, `failure-messages-vs-integration-2.txt` |
| `builder-probes/` | runner (`run-builder-probes.sh`), WS-4 observe runner copy, `derived/` (WS-2 chain-na, WS-3 unified + helper, WS-4 claim-time), `unedited/`, `derived-runs/`, `COMPARE-builder-probes.out` |
| `audit-probes/` | runner copy, `run-derived-probe.sh`, `derived/` (W12 g1-claim, AC16-X1 chain-na), `integrated/` (W12 unedited and derived; WS-3's and WS-5's D6 derived copies), `integrated-ws05/`, `COMPARE-audit-probes.out` |
| `g0/` | round-3 labels G0 probe and output |
| `slo-cost/` | R3-WS5-10 measurement script and output |
| `ws5-11/` | R3-WS5-11 reproduction script and output |

## 12. Process disclosures

- Model: Claude Opus 5 (1M context), `claude-opus-5[1m]`. Fresh context for this run. The session context was compacted
  once during the run, and work continued from the repository state. No sub-agents were used, and the owner was not
  contacted. I read no session or agent transcript, no task-output store (long commands were redirected to my own
  files) and no user auto-memory.
- `rm` is denied in this environment and was not retried. Superseded files were moved aside into the private scratch
  directory: the first WS-3 derived run (before change h; also kept in `derived-runs/` under its own name), the first
  W12 derived run (before its refusal reasons were recorded), and the first cost run (DRAFT tasks). Where a scratch
  directory could not be removed, a fresh name was used.
- One full certification run at `68f2e4a` gave 179/8. Seven of those failures were artefacts of my own editing
  `framework/policies/AUTHORITY_POLICY.yaml` and a migration file *during* the run: the canonical payload differed from
  the one the binary embeds. After that, framework files were never edited during a run. The eighth failure was a real
  test premise (the ws03_r3 unsealed-task record), which was fixed.
- A temporary diagnostic (`GOV_DEBUG_ADMIT`) was added to `scheduler/mod.rs` while finding the empty-alias defect and
  then removed. It is in no commit.
- While `run-builder-probes.sh` was executing (the WS-3 derived re-run and WS-4), I edited the script. Bash reads
  scripts incrementally, so it printed a syntax error after its last case. Both outputs had completed (each records its
  exit), and later runs used the saved script.
- The G0 probe (§7.5) ran while the final certification suite was running. Neither measures timing. The cost
  measurement (§7.6) ran with nothing else running.
