# P2-HO-0050 — Repair iteration 1, round 4: implement OD-P2-03 (gate only elevated tool installs)

| Field | Value |
|---|---|
| Handoff | P2-HO-0050 |
| From | Phase-2 orchestrator (routing only) |
| To | fresh `capability-repair` builder, run **P2-AR-0055** |
| Continues | P2-AR-0053's item R4-O1, which the owner has now decided (**OD-P2-03**) |
| Base | your worktree's commit: `phase2/repair-1-r4-residual-b` tip `d96c8ab` |
| Branch | `phase2/repair-1-r4-residual-c` (yours) |
| Output directory | `release/capability-baseline/repair-1/r4-residual/` (add `02-OD-P2-03-REPORT.md`; do not rewrite the earlier reports) |
| Run report | `release/orchestration/phase-2/AGENT_RUNS/P2-AR-0055.report.yaml` |
| Required verdict | `READY_FOR_INDEPENDENT_CAPABILITY_VERIFICATION`, `OWNER_DECISION_REQUIRED` or `INCOMPLETE` |

**Read first, in full:** `GATES/OWNER-DECISION-P2-0003-TOOL-INSTALL-GATE.md` (the decision and its seven implementation
requirements — this is your specification), `P2-HO-0048` and `P2-HO-0042`, the two earlier reports in your output directory
(`00-REPAIR-REPORT.md` §1 for the INT3-O1 mechanism, `01-CONTINUATION-REPORT.md` for R4-O1 and its evidence under
`evidence/r4-o1/`), `P2-HO-0031` (availability rule), `P2-HO-0020`, `P2-HO-0010`, and WS-7's round-3 report for IP-W7-1 /
BC-P2-41.

## Your scope

Exactly OD-P2-03 and nothing else. The owner decided:

- A tool installation proceeds **without** a Human Gate when the tool is authenticated/pinned, independently
  governed-reviewed, registered, reversible, **and stays entirely inside the project's already-authorised permission and
  trust envelope**.
- A Human Gate **is required** when the installation **expands authority**: privilege escalation; broader
  filesystem/project access; new secret or credential access; host-level authority; governance or security-policy mutation;
  a new or unrestricted network trust boundary.
- Ordinary network use already authorised by project or tool policy (approved registries, allowlisted services) does
  **not** by itself count as elevated.
- **Every** installation is recorded with its security and CIT evidence, gated or not.

The decision record's "What this requires of the implementation" items 1–7 are your acceptance requirements. In particular:
the envelope is computed from trusted OS state, never from the descriptor's own declarations (F4, BC-P2-39); anything that
cannot be evaluated fails closed and gated; the recorded change transaction states which branch applied and why; and
`ws07::a_governed_security_review_by_another_role_lets_the_installation_proceed` returns to asserting that no gate is
raised, with its tool inside the envelope.

P2-AR-0053's commit `ab0a075` implemented "always gate" and is superseded. Keep its change-control machinery where it
serves Contract v3 K3 — the OS-proposed change transaction, the CIT-E writer that re-derives and re-verifies the request,
the installation-authority checks, and the §6 acquisition sink asked at the instant of the write — and remove its
unconditional gating and its edit to that test. Do not weaken `TOOL_POLICY` or the policy-precedence rules to achieve this.

## Constraints

- Do not edit the round-4 evidence-map files owned by P2-AR-0042: `runtime/src/contracts.rs`, `framework/contracts/**`,
  `framework/schemas/governance-capability-acceptance.schema.json`, `tests/governance/capability-evidence-map.yaml`,
  `docs/generated/**`.
- **Do not rename, remove or `#[ignore]` any existing test** (the evidence map names 441 tests by path). New tests are
  expected — list each with what it proves, for the integrator and the evidence map.
- Tests must cover both branches: a non-elevated install closing with no gate; an install gated for **each**
  authority-expansion trigger; and one showing that ordinary allowlisted network use alone does not gate.
- Availability rule (P2-HO-0031) on what you touch; classify any new or changed subcommand in `COMMAND_GUARDS` / `g0_label`;
  mirror any schema version bump in `framework/KERNEL.yaml`.
- Re-establish on your final tree: `cargo build --release` (0 warnings), `cargo test --lib`, `cargo test --test
  certification` (chunking allowed if you show the union equals the full test list), the Python plugin tests, rustfmt on
  files you touch, and all four R1 held-out suites unedited through a private uniquely named path with the census.
  P2-AR-0053 measured lib 266/0, certification 200/0/0, census 123 files / 2340 functions, 0 §6 violations; baselines
  AR-0027 26/3, AR-0029 26/2 (`ho_f` does not compile), AR-0031 27/7, AR-0033 30/1 (size pin, judged on its property).
- `export CARGO_BUILD_JOBS=2`. Commit on your branch only; never check out, merge into, rebase, tag or push another branch;
  do not modify the main checkout. Do not read any agent transcript or task-output store. `rm` is denied — move files aside
  and say so.
- If implementing the decision as written turns out to need a **further** owner choice the decision does not make, return
  `OWNER_DECISION_REQUIRED` for that point alone, state it precisely, and finish everything else.

## Report

`02-OD-P2-03-REPORT.md`: how the envelope is computed and from which trusted sources; the rule as written in policy and the
governed record that carries it; the gated and non-gated paths with evidence for every trigger; what you kept and what you
dropped from `ab0a075`; files changed; tests added or changed with reasons; regression and R1 with census; remaining
integration points. Update `claims.yaml` with your item, sourced to `P2-AR-0055`.
