# P2-HO-0020 — Repair iteration 1, round 2: common protocol

Every round-2 repair builder reads this file **and** its own round-2 handoff.

## What is different from round 1

Round 2 starts from the **integrated round-1 tree** (all eight round-1 repairs merged by the integration builder P2-AR-0022;
report `release/capability-baseline/repair-1/integration/00-INTEGRATION-REPORT.md`). Everything in
`P2-HO-0010-repair-1-common-protocol.md` applies unchanged — who you are, what counts as a repair, preservation of R1 and
§6, integration rules for the shared crate, outputs and prohibitions — with these additions:

1. **Two kinds of work.** Each round-2 handoff lists (a) **classes** to repair (repair-delta §2 waves 2-3) and (b)
   **integration points (IPs)** that round-1 builders recorded against files you own. An IP is written in the originating
   builder's `release/capability-baseline/repair-1/<ws>/00-REPAIR-REPORT.md` (its "Integration points" section). Read it
   there. Implement each IP whose purpose still stands, **as a requirement, not a patch recipe**: if the recipe is wrong for
   the integrated tree, satisfy the IP's stated purpose another way and say so. If an IP is obsolete, say why.
2. **Owner decisions now in force** (read them): `release/orchestration/phase-2/GATES/OWNER-DECISION-P2-0001-AGENT-ROLE-IDENTITY.md`
   (agent roles stay adapter-declared — do not build agent credentials) and `OWNER-DECISION-P2-0002-UNPROVISIONED-MACHINES.md`
   (refuse external-source kernel ingress until provisioned). Orchestrator adjudication `P2-ADJ-0001-STANDALONE-HUMAN-GATE-ANCHOR.md`
   (standalone human-gate anchor off by default).
3. **New APIs you must use, not re-invent** (from round 1): role resolution and G0 (`authority::*`, `control::COMMAND_GUARDS`,
   `g0_label` — every new subcommand must be classified or it is refused); the T2 binding primitive (`t2::*`); verified gate
   answers and human approval (`gates::verified_answer`, `human_approval_for`, `task_gate_authorisation*`, `create_system`);
   the scheduler tier contract (`scheduler::{guard, tier_run, close_gate}`, `catalogue::ops`); the task-input manifest and
   receipt (`context::manifest::*`, `context::receipt::*`, `verify_delivery`, `ensure_dispatchable`); artefact identity and
   lineage (`graph::identity::*`, `graph::lineage::*`); installation posture (`srr::installation::*`); failure memory
   (`memory::failures::*`); oracle validation (`qualification_oracle::*`).
4. **Builder tests** must declare the role they need and answer gates through the owner-signed channel helpers
   (`tests/certification/ws03.rs`); never re-introduce a default role or an unauthenticated answer path.
5. **Nine builders run in parallel** (WS-2, WS-3, WS-4, WS-5, WS-6, WS-7, WS-8, WS-9/11, WS-10). File ownership is as in
   repair-delta §3, with the round-2 assignments stated in each handoff. `export CARGO_BUILD_JOBS=2`.
6. **Output directory**: `release/capability-baseline/repair-1/r2-<ws>/`; run report as named in your handoff.

A round-3 builder set, then a fresh integration builder, follow round 2. Nothing becomes a candidate until all rounds are
integrated; then `cap2-candidate-1` is minted and independently verified.
