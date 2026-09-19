# P2-HO-0041 — Repair iteration 1, round 4: WS-1 evidence map (BC-P2-02)

| Field | Value |
|---|---|
| Handoff | P2-HO-0041 |
| From | Phase-2 orchestrator (routing only) |
| To | fresh `capability-repair` builder, run **P2-AR-0042** |
| Base | the commit your worktree is checked out at (release branch with round 3 integrated, `e4cb662` or later) |
| Output directory | `release/capability-baseline/repair-1/r4-ws01/` |
| Run report | `release/orchestration/phase-2/AGENT_RUNS/P2-AR-0042.report.yaml` |
| Required verdict | `READY_FOR_INDEPENDENT_CAPABILITY_VERIFICATION`, `OWNER_DECISION_REQUIRED` or `INCOMPLETE` |

**Read first, in full:** `P2-HO-0031-repair-1-round-3-common.md` (availability rule), `P2-HO-0020-repair-1-round-2-common.md`,
`P2-HO-0010-repair-1-common-protocol.md`; the round-3 integration report
`release/capability-baseline/repair-1/integration-3/00-INTEGRATION-REPORT.md`; repair-delta
`release/capability-baseline/audit-0/synthesis/repair-delta.md` §0 and BC-P2-01/BC-P2-02; the frozen gate contract
`release/orchestration/phase-2/GATES/PHASE-2-FROZEN-GATE-CONTRACT.md` AC-10, AC-11, AC-13; Contract v3 lines 37–111
(`Governance_OS_Capability_Acceptance_Contract_v3.md`); round-1 WS-1 report `release/capability-baseline/repair-1/ws01-12/00-REPAIR-REPORT.md`
(IP-3 and how `gov contract compile`/`verify` treat governed fields).

## Scope

**BC-P2-02** (AC-10): every one of the 101 capabilities (100 numbered + Gate U) names at least one evidence owner that
**actually runs** — a G0…G6 tier check, an independent held-out suite, Human Decision Gate evidence, or release/clean-clone
evidence — with the Contract v3:53-73 governed fields populated (evidence class from :81-91, automated check/test ids,
health-scheduler tiers ⊆ G0–G6, freshness triggers ⊆ :97-109, independent-verification obligation, and the rest where the
source supports a value). `gov contract verify` enforces it: a capability with zero owners, an owner id that does not resolve
to a check/test that exists and runs, an out-of-vocabulary value, or a mutation of any governed field without recompile each
fail with a typed error.

This class closes last: it maps the owners the other workstreams built. You map; you do not change capability behaviour.

## Files you own this round

`runtime/src/contracts.rs`; `framework/contracts/**`; `framework/schemas/governance-capability-acceptance.schema.json`;
`tests/governance/capability-evidence-map.yaml`; `docs/generated/**`; new tests you add for the map
(e.g. `tests/certification/ws01r4.rs` plus its `mod` line). Declared additive exception, only if you add a `gov contract`
subcommand: its arms in `cli/src/main.rs` and its `COMMAND_GUARDS` entry / `g0_label` (a new subcommand must be classified
or G0 refuses it). A second round-4 builder (P2-AR-0043) works in parallel on other files; do not edit files outside this
list, and do not rename or remove any existing test (the map names them). If resolving an owner id needs a registry of check/test ids that does not
exist, build it inside your files (e.g. `contracts.rs` resolving `cargo test` names, scheduler check ids from
`scheduler::catalogue`, doctor ids, held-out suite paths) rather than editing other modules.

## What "actually runs" means

- A **tier owner** names a check id the scheduler catalogue declares at that tier (`scheduler::catalogue`), or a doctor id
  run by a tier; the map's tier must match the catalogue's.
- A **test owner** names a `cargo test` path that exists in `--lib` or `--test certification` (resolved, not string-matched
  by prefix only) and is not `#[ignore]`d.
- An **independent held-out owner** names a suite under `release/verification/**/heldout-tests/` or an obligation the
  frozen gate contract assigns to an independent verifier (AC-14 R1, AC-6 oracle review) — label it as independent, never
  as builder evidence.
- **Human-gate** and **release/clean-clone** owners name the command/record type that produces that evidence.
- An owner must exercise the capability, not merely touch its file. For a sample of owners per gate, show in your report
  that running the owner fails when the capability is broken (mutation or planted-fault evidence, labelled).

## Items routed to you

Every evidence-map integration point the builders recorded. Read each in its report; treat each as a requirement, not a
recipe, and check the named owners still exist in the integrated tree (tests were renamed/merged in integration rounds):

- Round 1: `ws01-12` IP-3; `ws02` IP-WS02-19; `ws04` IP-11; `ws05` IP-6 (and §5); `ws06` IP-1; `ws08` IP-5;
  `ws09-11` item 6 ("WS-1, evidence map").
- Round 2: `r2-ws02` R3-6; `r2-ws04` R2-14; `r2-ws05` IP-R3-8; `r2-ws06` IP-R2-4; `r2-ws08` IP-R2-WS08-11;
  `r2-ws09-11` IP-R2-6; `r2-ws10` IP-WS10-14.
- Round 3: `r3-ws04` IP-R3-WS04-10; `r3-ws06` IP-R3-WS06-6; `r3-ws08` IP-R3-WS08-10; `r3-ws09-11` IP-R3-WS09-5; any other
  evidence-map row in the round-3 reports and in `integration-3` §8.
- All reports are under `release/capability-baseline/repair-1/<dir>/00-*.md`.

Where no builder named an owner for a capability, find the check/test that exercises it in the integrated tree. Where none
exists, do **not** invent one: record the capability with the owner it would need, `evidence_class` as the contract allows,
and list it in your report as a gap for the verifier (it is then honestly unmapped, and `gov contract verify` must report it
as such — zero owners is a failure, not a silent pass).

## Also required

- The map must stay semantically faithful to the owner source (AC-13): `gov contract compile` preserves governed fields;
  `gov contract verify` still refuses every round-1 mutation control.
- AC-10's second sentence (changing a relevant input invalidates prior green evidence) is BC-P2-03's and already built;
  record which owner proves it for each freshness-trigger class you map.
- Produce the regenerated suite-to-contract matrix (every capability → owners → tier → last-run evidence) as
  `release/capability-baseline/repair-1/r4-ws01/suite-to-contract.md` (+ machine-readable), generated from the product's
  own map by the product (a `gov contract` subcommand or `contracts.rs` function), not hand-written.
- Regression and R1 exactly as the common protocols require (private path, census).

Report as before: per-item claims, owners per capability (counts by class and tier), unmapped gaps, mutation controls,
regression and R1 counts with census, remaining integration points.
