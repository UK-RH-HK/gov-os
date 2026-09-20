# P2-HO-0049 — Repair iteration 1, round 4: integration builder

| Field | Value |
|---|---|
| Handoff | P2-HO-0049 |
| From | Phase-2 orchestrator (routing only) |
| To | fresh `capability-repair` **integration builder**, run **P2-AR-0054** — not any earlier builder or integrator |
| Base | the commit your worktree is checked out at (release branch with round 3 integrated and both round-4 runs recorded) |
| Branches to merge | `phase2/repair-1-r4-ws01` (P2-AR-0042, evidence map; tip `d1487e8`) and `phase2/repair-1-r4-residual-c` (tip `854980c`: P2-AR-0043's residual IPs + P2-AR-0053's continuation + P2-AR-0055's OD-P2-03 implementation) |
| Output directory | `release/capability-baseline/repair-1/integration-4/` |
| Run report | `release/orchestration/phase-2/AGENT_RUNS/P2-AR-0054.report.yaml` |
| Required verdict | `READY_FOR_INDEPENDENT_CAPABILITY_VERIFICATION` or `INCOMPLETE` |

Method exactly as `P2-HO-0040-integration-3.md`, `P2-HO-0030-integration-2.md` and `P2-HO-0019-integration-1.md` (read them
and the three prior integration reports under `release/capability-baseline/repair-1/integration{,-2,-3}/`). Rules of
P2-HO-0031 (availability rule), P2-HO-0020 and P2-HO-0010 apply, including the R1 private-path census rule. Read both
round-4 reports first: `r4-ws01/00-REPAIR-REPORT.md`, and `r4-residual/00-REPAIR-REPORT.md`, `01-CONTINUATION-REPORT.md`, `02-OD-P2-03-REPORT.md` and `claims.yaml`. Read
`GATES/OWNER-DECISION-P2-0003-TOOL-INSTALL-GATE.md` too: OD-P2-03 is in force, and a review-evidenced installation **inside**
the project's authorised envelope raises **no** human gate, while one that expands authority does (R4-IP-1 as revised by
P2-AR-0055). Do not re-litigate it.

This is the last repair round of iteration 1. The tree you produce becomes **`cap2-candidate-1`**, which fresh independent
verifiers then grade against the frozen gate contract. Integrate; do not open new work.

## Required reconciliation

1. **The evidence map versus the residual branch's tests (IP-R4-WS01-3, integration-critical).** P2-AR-0042's map names
   441 tests by path and `gov contract verify` resolves every one of them against the test harnesses' module trees. The
   residual branch adds tests (`tests/certification/r4_residual.rs` and others) and changed existing test bodies. After
   merging, `gov contract verify` **must pass**: if it reports `CONTRACT_EVIDENCE_OWNER_UNRESOLVED` or
   `CONTRACT_EVIDENCE_MAP_NOT_RECOMPILED`, follow P2-AR-0042's documented route — update
   `release/capability-baseline/repair-1/r4-ws01/evidence/mapping/owner-spec.yaml`, run its `apply_owner_spec.py`, then
   `gov contract compile` — and map the residual run's new tests to the capabilities their own report names. Do not delete
   an owner to make verify pass, and do not rename or `#[ignore]` a test.
2. **Overlapping files.** Both branches changed `cli/src/main.rs` and `runtime/src/orchestration/control.rs` (P2-AR-0042
   additively: the `contract matrix` arm and its guard entry; the residual branch: its own subcommands and guards).
   Reconcile both, and check every new or changed subcommand is classified in `COMMAND_GUARDS` / `g0_label`.
3. **`gov contract matrix`** regenerates the suite-to-contract matrix on the integrated tree: run it from the integrated
   run's own lib, certification, R1, G5 and doctor outputs, and put it in your evidence directory. Report the owner census
   and how the counts moved from P2-AR-0042's (441 PASSED / 174 RAN / 37 NOT_IN_SUPPLIED_EVIDENCE / 110 OBLIGATION).

## Carry forward, do not close here unless integration itself requires it

- P2-AR-0042's disclosed gaps (16 capabilities owned only by builder tests; 9 with no G-tier owner; no G6 owner; 127
  checklist items unowned) and its IPs `IP-R4-WS01-1`, `-2`, `-4`, `-5`, `-6`.
- Everything the residual reports list as not done: R4-O2 (`gov plugins unregister` writes the sealed registry directly and
  no tool de-installation path exists), R4-O3, R4-O4 (cit schema 1.3.0 vocabulary — confirm schema-version handling with the
  WS-9 migration surface), R4-O5 (policy documents at 1.1.0: an older adopted kernel has neither new key and therefore gates
  every installation — the intended fail-closed default; check the migration path says so), R4-O6 (optional), plus INT3-O4 (legacy unsealed records reported, never blessed) and R3-WS5-11 (not reproduced).
- Record them in your report as remaining integration points for the verifiers; the orchestrator routes them onward.

## Evidence required

- `cargo build --release` (0 warnings), `cargo test --lib`, `cargo test --test certification` (chunking allowed if you show
  the union equals the full test list), the Python plugin tests, rustfmt on files you touch, and `gov contract verify`.
- All four R1 held-out suites, unedited, through a private uniquely named path, with the census; AR-0033 `hv_a::a1` is
  judged on its property (run its census with only the size assertions removed, labelled). Baselines: AR-0027 26/3;
  AR-0029 26/2 (`ho_f` does not compile); AR-0031 27/7; AR-0033 30/1.
- Both builders' own probes on the integrated binary, unedited where their surface still exists and through labelled derived
  copies otherwise, as previous integrations did.
- The integrated `product_code_digest` and `governed_state_digest`
  (`python3 release/orchestration/phase-2/tools/product_identity.py <commit>`).

Report as before: `00-INTEGRATION-REPORT.md` with every product change beyond the merges and its reason, test counts, R1
counts with census, `gov contract verify` and matrix results, integration regressions against the builders' own probes,
stopped items, and remaining integration points. `export CARGO_BUILD_JOBS=2`. Commit on your branch only; do not merge into
`release/4.1.6-rc1`, rebase, tag or push. `rm` is denied — move files aside and say so.
