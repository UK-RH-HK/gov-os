# P2-HO-0040 — Repair iteration 1, round 3: integration builder

| Field | Value |
|---|---|
| Handoff | P2-HO-0040 |
| From | Phase-2 orchestrator (routing only) |
| To | fresh `capability-repair` **integration builder**, run **P2-AR-0041** — not any earlier builder or integrator |
| Base | the commit your worktree is checked out at (release branch with every round-3 run report and outcome recorded) |
| Branches (all from base `53897c1`) | `phase2/repair-1-r3-ws03` (P2-AR-0034), `-ws08` (P2-AR-0039), `-ws05` (P2-AR-0036), `-ws04` (P2-AR-0035), `-ws02` (P2-AR-0033), `-ws06` (P2-AR-0037), `-ws07` (P2-AR-0038), `-ws09-11` (P2-AR-0040) |
| Output directory | `release/capability-baseline/repair-1/integration-3/` |
| Run report | `release/orchestration/phase-2/AGENT_RUNS/P2-AR-0041.report.yaml` |
| Required verdict | `READY_FOR_INDEPENDENT_CAPABILITY_VERIFICATION` or `INCOMPLETE` |

Method exactly as `P2-HO-0019-integration-1.md` and `P2-HO-0030-integration-2.md` (read both, and the two prior integration
reports under `release/capability-baseline/repair-1/integration{,-2}/`). Rules of `P2-HO-0031`, `-0020`, `-0010` apply,
including the **availability rule** (P2-HO-0031) and the R1 private-path census rule.

## Required reconciliation: ONE P2-ADJ-0002 mechanism

WS-3 (P2-AR-0034) and WS-8 (P2-AR-0039) each built a complete provisioning mechanism for cross-machine T2 continuity:
WS-3 — owner-signed `t2-binding-authority` for a per-owner HMAC key, `gov trust t2-binding --provision <bundle>`, v2 seals
(`hmac-sha256/t2-v2`) binding authority/machine/operation/time/content, `--reseal`, verification against the current trusted
root; WS-8 — `srr/binding.rs`, root-delegated `t2-binding` authority document by key id/commitment, `gov trust bind`,
`srr::binding::keyring()` as the use-time API (retired keys stay honoured after rotation; unverifiable authority refused),
and the two-machine harness (`clone_to_machine`, machine kinds Owner/AnchorOnly/Unprovisioned/ForeignOwner). Both use a
root-delegated `t2-binding` role, commitments only, and **no signing inside `gov`** (SRR-R0-L4; R1 held-out d6/f2/d7).

Unify them into **one** delegation role, **one** authority document format, **one** provisioning command, **one** keyring
API, consumed by `t2.rs` sealing/verification, with rotation/revocation semantics from the stronger of the two. Keep every
property either builder's tests assert (portable between the owner's bound machines; FOREIGN/UNAUTHORISED/BROKEN/typed
refusals otherwise; nothing secret in any repository; refusal below floor, from a repository, via environment, on an
unprovisioned machine, with a wrong signer, expired/older/mismatched authority). Remove the redundant surface rather than
leaving two paths that can disagree. Describe the chosen shape and why in your report. This is a reconciliation of two
implementations of one determined requirement (P2-ADJ-0002), not a new design decision; if the two genuinely cannot be
reconciled without choosing a trade-off the sources leave open, stop that item and state it precisely.

## Other known round-3 integration items

- `governance/registry/` into `tasks::OS_MANAGED_PREFIXES` (WS-7 IP-W7R3-1 — **required**: plugin registration inside a claimed
  task is otherwise refused at close; WS-3 IP-R3-WS03-3). WS-5 did not add it (checked on `phase2/repair-1-r3-ws05`).
- **IP-R3-WS04-01 (integration-critical):** `gates::answer`/`revoke` write CIT records without re-sealing, so a CIT declined inside another task's claim window fails that task's close (`MUTATION_SCOPE_VIOLATION`). In order: apply WS-4's `release/capability-baseline/repair-1/r3-ws04/evidence/IP-R3-WS04-01.gates-reseal.patch` (or an equivalent re-seal of previously-verified CIT records in `gates.rs`), then add `cit` to `t2::SEALED_RECORD_TYPES` (WS-3 IP-R3-WS03-2), then un-ignore `ws04r3::a_cit_declined_during_another_tasks_claim_does_not_block_its_close`. WS-4 measured the end state at lib 215/0, certification 145/0.
- **WS-5 round 3 (P2-AR-0036, report `r3-ws05/00-REPAIR-REPORT.md` §7.2), in addition:**
  - **Task-record sealing (WS-5 r2 IP-R3-1, final step — integration-critical, ordered):** only after WS-3's and WS-4's
    re-sealing of the task records they rewrite is merged, seal task records on every OS write (including generated tasks
    written by `orchestration::generation`) and add `task` to `t2::SEALED_RECORD_TYPES`. Doing it earlier makes their unsealed
    rewrites refusable at close. Prove it with a close inside another task's claim window.
  - Declared additive exceptions to review under WS-3's role/guard semantics: `TaskCmd::Generate`, its `g0_label` and `run`
    arms and the post-command `generation::after_command` hook in `cli/src/main.rs` (R3-WS5-1); `task generate` (Write,
    `replan_tasks`) and `task generate --dry-run` (Read) in `COMMAND_GUARDS` (R3-WS5-2); `pub mod generation;` (R3-WS5-3).
    The post-command hook must respect the availability rule and must not run for commands the guard refused.
  - CLI `task show` calls `orchestration::tasks::show` (R3-WS5-4).
  - The claims store moved to `paths::store_path(root, "claims")`: the scheduler sandbox, currency input and doctor D017/D026
    must read it there (R3-WS5-5; WS-6 IP-R2-12) — WS-2's `2e72007` already moved the sandbox copy; check the rest. Emergency-control state to `store_path(root, "emergency-control")` with
    `relocate_legacy` (R3-WS5-6; WS-6 IP-R2-8) unless WS-3/WS-6 already did it — D6-b2-B must pass.
  - `recovery::recover` writes report `evidence`/`discoveries`/`unresolved` items as strings per the report schema (R3-WS5-7,
    HIGH, pre-existing): a recovery report must pass `schema_invariants` with remediation work closed, not only while it is open.
  - OS writes made into governed records inside another task's claim window (`cit::propagation` markers incl. those
    `detect_and_propagate` now writes at claim; `lifecycle::record_influence`) are attributed (seal or recorded write set) so
    close never reads them as the worker's mutations (R3-WS5-8) — same family as IP-R3-WS04-01; solve both with one mechanism.
  - `KERNEL.yaml` `schema_versions`: `task` 1.2.0, `test-obligation` 1.1.0 (R3-WS5-9; falls under the kernel-mirroring item below).
  - Measure the per-write generation/reconciliation and claim-time checkpoint cost against the Gate U SLOs and report it
    (R3-WS5-10); the sandbox `memory_retrieval_regression` symbol route returning nothing (R3-WS5-11, pre-existing): fix if in
    reach, otherwise report it as stopped with the evidence.
  - Integration regression check: WS-5 changed existing tests in greenfield, repair, repair2, ws03, ws04r2, ws05 and ws06
    (report §8); re-check every other builder's tests that create, claim or close tasks, because generation now runs after
    every governed write and new generated tasks take the next sequential id.
- **WS-2 round 3 (P2-AR-0033, report `r3-ws02/00-REPAIR-REPORT.md` §6), in addition:**
  - **One availability host API (integration-critical).** WS-2 replaced the scheduler host surface (`scheduler::{Request,
    admit, confirm_remedy, guard, subjects_reach}`, catalogue `BlockRule{min_severity, operations, scope, remedies}`,
    `BlockScope::{Global, CoveredPaths, Subjects}`, `WORK_REMEDIES`/`ALL_REMEDIES`, `ops::COMMITTING`/`UPDATE_SUBJECTS`) while
    WS-5 wired the availability rule into `tasks::create`/`claim`/`close` (`guard_work`) against the round-2 API. Converge
    every host on WS-2's API, passing the task id and its declared inputs as subjects at create and claim (IP-R3-WS02-03), so
    that subject-scoped blocks leave independent claims available at the host as well as in the decision.
  - Drop `cit propose` from `control::GOVERNED_WORK_OPS`; the CIT host already guards it with its paths (IP-R3-WS02-01, WS-3
    file) — this is the one failing WS-2 supplementary line, AV.2b-e2e.
  - `update::apply_update_opts`: `admit(UPDATE_APPLY, UPDATE_SUBJECTS)` after `authority::require`, then `confirm_remedy` before
    committing, rolling back on `HEALTH_REMEDY_INCOMPLETE` (IP-R3-WS02-02, WS-8 file). Check it against WS-8's own round-3
    update/G5 changes.
  - CIT `guard_paths` include the manifest's file targets, so a CIT repairing a file-level block reaches its subjects
    (IP-R3-WS02-04, WS-4 file). Optional: CIT-E repair refuses at entry when `details.remedy_admissible` is not true (-11).
  - WS-4 R2-1 `require_current_inputs` at close and R2-3 `detect_and_propagate` at claim were done by WS-5 this round
    (IP-R3-WS02-05/-06): after merging, re-run zeta-r `W12-G1-dependency-evidence-invalidated` and AC16-X1 `X1-G1xW6` and
    report both (they close BC-P2-07's remaining line).
  - `records.rs` maps `revalidates`→`TESTS` (task → task), which `memory::integrity` TESTS signatures refuse, so every
    generated revalidation task raises a false `ill_typed` finding (IP-R3-WS02-07). Fix the mapping or the signature, one
    way, and prove a CIT that invalidates DONE work leaves `graph_integrity`/D015 clean.
  - The recovery report writer (IP-R3-WS02-08) is the same defect as R3-WS5-7 above; fix once.
  - Once the BC-P2-31 stores have moved, raise `misplaced_os_state` to `medium` (IP-R3-WS02-09); WS-6's R3-4 heading markers
    in `memory::coverage` let WS-2's confirmation step go (-10).
  - Orchestrator adjudication **P2-ADJ-0003** (`GATES/P2-ADJ-0003-H4-GAPS-AND-GREEN-PRECONDITIONS.md`): H4 gaps keep degrading
    suite health and refuse nothing; do not lower their severity. Probe preconditions that need a green baseline use a
    contract-valid (H4-complete) fixture.
- WS-10's research write commands: declare `record_research_evidence: L1`, `lifecycle::RECORD_AUTHORITY` and the 12
  `COMMAND_GUARDS` entries together (WS-3 IP-R3-WS03-4).
- Kernel version 4.1.6 (WS-8): every schema version bumped by any round-3 builder must be mirrored in `KERNEL.yaml`
  (`release build` and tests refuse drift — WS-8 IP-R3-WS08-7); `health` joins `payload_dirs` only once WS-2's planted
  literal is gone and the kernel's own scanner finds the payload clean (IP-R3-WS08-5).
- Product-release records: WS-8's `release::record` + WS-4's record type + WS-3's `release record` G0 class → wire the CLI arm if
  all three parts are present (IP-R3-WS03-5 / IP-R3-WS08-8).
- WS-6's declared deviation: two existing `cli/src/main.rs` lines pass `observe_boundaries: true` on `rebuild-memory` /
  `memory rebuild` — review under WS-3's CLI semantics; keep unless it breaks a guard/freeze property.
- Template/migration convergence: WS-6's reordered `REPOSITORY_CONTRACT` template reaches installed projects through WS-9's
  `sync_overlay_template` in `M-4.1.5-4.1.6` (IP-R3-WS06-1, IP-R3-WS09-2); `common::tree_hash` should exclude `.governance-state/**`
  (IP-R3-WS09-3).
- Stores relocated this round (control state, registry, claims, migration/update/CIT snapshots): WS-6's relocation test must pass;
  every writer uses `paths::store_path`.
- Converge test setup on the one harness (WS-8 `common.rs`, with the two-machine helper) exactly as round 2 did.

Report as before: integrated `product_code_digest`, every product change beyond the merges with reason, test counts, R1
held-out counts with census, integration regressions vs builders' own probes, stopped items.
