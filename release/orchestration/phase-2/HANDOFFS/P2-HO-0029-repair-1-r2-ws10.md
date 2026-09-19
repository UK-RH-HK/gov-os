# P2-HO-0029 — Repair iteration 1, round 2: WS-10

| Field | Value |
|---|---|
| Handoff | P2-HO-0029 |
| From | Phase-2 orchestrator (routing only) |
| To | fresh `capability-repair` builder, run **P2-AR-0031** |
| Workstream | WS-10 |
| Base | the commit your worktree is checked out at (integrated round-1 tree) |
| Output directory | `release/capability-baseline/repair-1/r2-ws10/` |
| Run report | `release/orchestration/phase-2/AGENT_RUNS/P2-AR-0031.report.yaml` |
| Required verdict | `READY_FOR_INDEPENDENT_CAPABILITY_VERIFICATION`, `OWNER_DECISION_REQUIRED` or `INCOMPLETE` |

**Read first, in full:** `P2-HO-0020-repair-1-round-2-common.md`, then `P2-HO-0010-repair-1-common-protocol.md` (all of it
applies), then `release/capability-baseline/audit-0/synthesis/repair-delta.md` §0, §2, §3 and every class named below with
the findings and probes it cites, then the round-1 integration report
`release/capability-baseline/repair-1/integration/00-INTEGRATION-REPORT.md`.

## Classes

BC-P2-46 (scenario → data → test-data lineage; test-data author independence recorded and checked; data provenance required and read), BC-P2-47 (research record completeness — method, sources, measurements, uncertainty, conclusion, confidence, influenced decisions; incomplete research cannot be cited as evidence), BC-P2-48 (experiment lifecycle — hypothesis, method/data, reproducibility, results, interpretation, decision influence, production merge prohibited where experimental).

## Files you own this round

a new research/experiment/test-data lifecycle module (e.g. `runtime/src/research.rs` or `runtime/src/lifecycle/**`); `framework/schemas/{research,experiment,scenario}.schema.json`; additive CLI subcommands in `cli/src/main.rs` (classified in `g0_label`/`COMMAND_GUARDS`); additive `pub mod` in `runtime/src/lib.rs`.

## Integration points routed to you

- **BC-P2-48 × WS-5:** round 1 made experiment tasks' production merge refused at close (`PRODUCTION_MERGE_NOT_ALLOWED`, ws05) and WS-2 will report detected merges. You build the experiment **lifecycle** (states, required fields, reproducibility evidence, decision influence) and expose what WS-5's close and WS-2's family consult; do not edit `tasks.rs`.
- **BC-P2-46 × WS-4:** lineage edges use WS-4's `graph::identity`/`lineage` APIs and `Record::edges()`.
- **BC-P2-47 × WS-2:** WS-2's `SKL-RESEARCH-BENCHMARK V1` scenario check is written and deferred until research completeness is enforced (IP-WS02-21) — make it true; WS-2 flips it to executable in round 3 (record the IP).
- Use WS-3's gate APIs where a human decision is required.

## Notes

This workstream was not in round 1; read `repair-delta.md` classes 46-48 and the delta-r J1/J2 and gamma-r H4 evidence in full.
