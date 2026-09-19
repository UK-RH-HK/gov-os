# P2-HO-0031 — Repair iteration 1, round 3: common protocol

Every round-3 repair builder reads this file **and** its own round-3 handoff.

Round 3 starts from the **integrated round-2 tree** (round-2 integration P2-AR-0032, report
`release/capability-baseline/repair-1/integration-2/00-INTEGRATION-REPORT.md`). Everything in
`P2-HO-0020-repair-1-round-2-common.md` and `P2-HO-0010-repair-1-common-protocol.md` applies unchanged, including rule 7 of
P2-HO-0020 (R1 held-out re-runs through a private path measuring **your** tree, census recorded).

## What round 3 is

The last repair round before the evidence map (round 4) and candidate `cap2-candidate-1`. It closes:
1. the remaining dependency-wave classes (BC-P2-07 tier duties, BC-P2-23 W11 metrics, BC-P2-24 work generation,
   BC-P2-44 SLOs and the HEALTHY conjunction, BC-P2-13 in-task hook, BC-P2-31 writer moves);
2. every **round-3 integration point** the round-2 builders recorded against your files — each round-2 report
   `release/capability-baseline/repair-1/r2-<ws>/00-REPAIR-REPORT.md` has a "new integration points for round 3" section
   (also in its `claims.yaml`/run report); your handoff names the ones routed to you by ID;
3. two orchestrator adjudications: **P2-ADJ-0002** (T2 cross-machine continuity — `release/orchestration/phase-2/GATES/P2-ADJ-0002-T2-CROSS-MACHINE-CONTINUITY.md`)
   and the **availability rule** below.

## Availability rule (from Contract v3 L4 and O5; binding on every host and on the scheduler)

Contract v3 L4: *"Independent runnable branches continue. Global stop only when policy or critical-path state requires."*
O5: *"hard-block vs warning semantics are explicit"*. Round 2 surfaced four ways a health block refuses more than it
should: a block refusing the very operation that remedies it (brownfield D014 vs the repairing CIT; D006/D007 vs
`update --apply`; §5 routes); a single graph_integrity HIGH finding refusing **every** claim in the project; a governance
close refused by the gaps it closes; and the update entry guard refusing the update that adds the missing file. Required:
a hard-block refuses the operations whose reliance it protects, **scoped** to what the failing check governs; work that
remedies a block, and independent work outside the block's scope, stays available; a remedy that does not clear its
block does not commit; every refusal is typed and names the block and its scope. This must not re-open any refusal a
repair-delta class requires, nor any R1/§5/§6 property.

## Everything else

Same as round 2: requirements, not probe special-cases; use existing APIs; own-file edits plus declared additive
exceptions (new subcommands classified in `g0_label`/`COMMAND_GUARDS`); `export CARGO_BUILD_JOBS=2`; keep `cargo test
--lib` and `cargo test --test certification` green; the one provisioned-root harness convention (WS-8) for tests; never
re-introduce a default role, an unauthenticated answer path or the standalone human-gate anchor. Output
`release/capability-baseline/repair-1/r3-<ws>/` and the run report named in your handoff.
