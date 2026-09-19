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
  task is otherwise refused at close; WS-3 IP-R3-WS03-3) unless WS-5 already did it.
- `cit` into `t2::SEALED_RECORD_TYPES` once every CIT write is sealed (WS-3 IP-R3-WS03-2, WS-4's round-3 work).
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
