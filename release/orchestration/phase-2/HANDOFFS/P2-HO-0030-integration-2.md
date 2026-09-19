# P2-HO-0030 — Repair iteration 1, round 2: integration builder

| Field | Value |
|---|---|
| Handoff | P2-HO-0030 |
| From | Phase-2 orchestrator (routing only) |
| To | fresh `capability-repair` **integration builder**, run **P2-AR-0032** — not any round-1/round-2 builder or the round-1 integrator |
| Base | the commit your worktree is checked out at (release branch with every round-2 run report and outcome recorded) |
| Branches to integrate (all from base `843d79c`) | `phase2/repair-1-r2-ws03` (P2-AR-0024), `-ws08` (P2-AR-0029), `-ws05` (P2-AR-0026), `-ws04` (P2-AR-0025), `-ws02` (P2-AR-0023), `-ws06` (P2-AR-0027), `-ws07` (P2-AR-0028), `-ws09-11` (P2-AR-0030), `-ws10` (P2-AR-0031) |
| Output directory | `release/capability-baseline/repair-1/integration-2/` |
| Run report | `release/orchestration/phase-2/AGENT_RUNS/P2-AR-0032.report.yaml` |
| Required verdict | `READY_FOR_INDEPENDENT_CAPABILITY_VERIFICATION` (integrated tree builds and every suite is green) or `INCOMPLETE` |

## Who you are and the task

Exactly as in `P2-HO-0019-integration-1.md` (read it: merge `--no-ff` in the listed order, union textual conflicts,
register every new subcommand with WS-3's G0 guard at its true class, reconcile semantic conflicts minimally without
weakening any check/schema/test or re-introducing a default role or unauthenticated answer path, run everything, re-run
each builder's own probes against the integrated binary, report). The round-1 integration report
`release/capability-baseline/repair-1/integration/00-INTEGRATION-REPORT.md` shows what a good integration looks like.
Read `P2-HO-0020-repair-1-round-2-common.md` and `P2-HO-0010-repair-1-common-protocol.md` — their rules apply.

## Known round-2 integration items

- **Test-setup overlap.** WS-8 moved the certification harness to a provisioned throw-away root (`tests/certification/common.rs`
  helpers, setup edits in 12 test files); WS-3, WS-5, WS-7 and WS-9 each also edited test setup (gate answers through the
  owner-signed channel, provisioned roots, designated roles, sealed reports) in overlapping files (`update.rs`, `repair.rs`,
  `repair2.rs`, `repair3.rs`, `greenfield.rs`, `brownfield.rs`, `migration.rs`, `ws03.rs`, `failure_injection.rs`, `arch.rs`,
  `upstream.rs`, `common.rs`, `main.rs`). Converge them on **one** harness convention — WS-8's provisioned root with
  `human-gate` delegated to the test owner (WS-3 IP-R2-4) — keeping every asserted property of every version.
- **Remove WS-2's temporary D032 relaxations.** `brownfield.rs`, `migration.rs`, `repair2.rs` accept doctor D032 only as the sole
  failure on an UNPROVISIONED machine (WS-2 R3-7). With the provisioned harness merged, those machines are provisioned: remove
  the relaxation and confirm the tests pass without it. If a scenario is deliberately unprovisioned, it must assert the
  refusal/marking, not tolerate it.
- **Standalone human-channel anchor.** P2-ADJ-0001 (WS-3) turned it off; probes or tests from other workstreams written against the
  old default (e.g. WS-10's probe notes) must use the provisioned root, not re-enable the anchor.
- **Guard registration.** New subcommands from WS-2 (`health qualify`), WS-6 (`memory integrity`, `memory profile`,
  `memory select --gate`), WS-10 (research/experiment/scenario commands), WS-3 (`memory miss|failures`) and any from WS-4:
  confirm each is classified once, at its true class, and that `ws03::every_cli_command_label_is_classified_by_g0` passes.
- **R1-sensitive surfaces changed by several builders:** `srr/{verifier,installation,staging}.rs` (WS-8), the §6 sinks touched by
  WS-5 (`tasks::release` guard) and WS-7 (acquisition). Run every R1 held-out suite unedited through a **private path measuring
  the integrated tree** and record the census.
- **Secret-like literal.** WS-8 found an `AKIA…EXAMPLE` literal in WS-2's `framework/health/SKILL_SCENARIO_CHECKS.yaml` that the
  kernel's own scanner flags if installed. Do not change its semantics here (WS-2 round 3), but make sure no integrated
  test installs it into a scanned project.

## Output

`release/capability-baseline/repair-1/integration-2/00-INTEGRATION-REPORT.md`, `evidence/`, and your run report naming the final
work commit; report the integrated `product_code_digest`, every product change beyond the merges with its reason, test counts,
R1 held-out counts with census, integration regressions against each builder's own probes, and anything you stopped on.
