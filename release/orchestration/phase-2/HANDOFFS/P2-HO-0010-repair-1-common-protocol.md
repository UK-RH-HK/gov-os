# P2-HO-0010 — Repair iteration 1, round 1: common protocol for capability-repair builders

Every round-1 repair builder (P2-AR-0014 … P2-AR-0021) reads this file **and** its own workstream handoff.

## Context

`cap2-candidate-0` was rejected by the fresh independent synthesis P2-AR-0007
(`GOVERNANCE_CAPABILITY_BASELINE_REJECTED`, 134 blocking findings in 52 blocker classes BC-P2-01…52). The requirements
are in `release/capability-baseline/audit-0/synthesis/repair-delta.md` — **read §0 and every class your handoff names, in
full**. The classes, their findings and evidence are in `blocker-classes.yaml`, `findings.yaml` and the six family audits
of record under `release/capability-baseline/audit-0/*-r/` (their `evidence/` probes are runnable).

Repair runs in dependency rounds (repair-delta §2). Round 1 takes the classes with no unmet cross-workstream dependency,
eight builders in parallel from the same base commit. Later rounds build on the integrated result. Nothing is a candidate
until every round is integrated; then a new immutable candidate `cap2-candidate-1` is minted and **independently**
verified (R1 preservation AC-14, oracle-format review AC-6, fresh capability verification with fresh held-out tests).

## Who you are

A **capability-repair builder**. You implement. You never grade your own work: your evidence is regression evidence
(Contract v3 O3), and acceptance is decided later by fresh independent verifiers you will never see. Do not claim any
class is "accepted", "verified" or "closed" — claim `REPAIRED_CLAIMED` with evidence, or `NOT_REPAIRED` with the reason.

## What counts as a repair

- **Requirements, not probes.** Each class states what must become true, with its normative source. Satisfy the
  requirement generally. *"A repair that makes a probe pass by special-casing the probe's fixture is not a repair"*
  (repair-delta §0.3). Later verifiers will write fresh attacks you have not seen.
- **Evidence owner in the product.** Where a class requires a check that runs at a G-tier, add it to the product so it
  actually runs (repair-delta §0.2c). Where you add a product test, it is regression evidence.
- **Re-run the named probes.** For each class, re-run the audit-of-record probes the repair delta names and record
  before/after lines in your report. Run them from the merged evidence directories, unedited.
- **Fail closed, typed, observable.** New refusals are typed errors with remediation text, consistent with API-0002.
- **Stay inside accepted architecture.** ARCH-0001 and ARCH-0003 (owner-adopted) and the active decisions bind you. If a
  class cannot be satisfied without changing an accepted architecture/trust boundary, a new external dependency class, a
  security/availability/usability/cost trade-off the sources leave open, or owner-controlled material — **stop that
  class**, write the precise question into your report under `owner_decision_required`, and continue with the rest.
  Two such questions are already with the owner and are out of your scope: **OD-P2-01** (whether the OS binds *agent*
  L0–L4 role identity) and **OD-P2-02** (whether an unprovisioned machine may admit privileged kernel material).

## Preserve what holds

- **R1 (AC-14).** The Signed Release Root acceptance must remain valid. Do not weaken any SRR control. If your change
  touches `runtime/src/srr/**`, `kernel_trust.rs`, `kernel.rs`, `lock.rs`, `init.rs`, `update.rs`, `release.rs`,
  `recovery.rs`, `records.rs` (the record-write sink), `tools.rs`/`capabilities/**` (acquisition), or any §6 effect sink,
  run every prior R1 held-out suite unedited — `release/verification/4.1.6-r1/`, `-r1-2/`, `-r1-3/`, `-r1-4/`
  `evidence/heldout-tests/` (each is a standalone crate depending on `gov-runtime` by path; run it against your worktree)
  — and report the counts against their recorded baselines. `tests/certification/section6.rs` (the §6 derivation) must
  stay green; if you add a function performing a §6 effect, it must be caught by or conform to that derivation.
- **Regression.** `cargo test --lib` and `cargo test --test certification` must pass at your final commit. If an intended
  behaviour change breaks an existing builder test, update the test and state exactly why in your report; never weaken a
  test merely to pass it. `cargo fmt` the files you touch.
- **Contract source.** Never edit `Governance_OS_Capability_Acceptance_Contract_v3.md` or its canonical import bytes.

## Integration rules (eight builders share one crate)

- **Own your files.** Edit only the files your handoff assigns (repair-delta §3 table). Exceptions, all additive:
  - `cli/src/main.rs` — semantic changes (role resolution, guards) belong to WS-3 only. Others may **add** new subcommands,
    flags and match arms for their own features in a self-contained block, changing no existing line except where an
    append requires it. List every such addition in your report as an integration point.
  - `runtime/src/lib.rs` — add `pub mod` lines only.
  - `runtime/src/records.rs` — WS-4 edits only the relation-fields/edges region; WS-6 only the record-text/chunk region.
  - A file owned by a workstream **not** in this round (e.g. `runtime/src/orchestration/tasks.rs` for task-close hooks,
    `runtime/src/doctor.rs` for new doctor checks when you are not WS-2) — do **not** edit it. Expose a clean API on your
    side and record the **integration point** (file, function, the exact call to add, and why) in your report; a later
    round wires it.
- **Cross-workstream dependencies.** Where a class needs another workstream's not-yet-merged work, implement your side
  against a clear API, record the dependency, and do not implement the other side.
- **Build hygiene.** Use your worktree's own `target/`. Limit parallelism: `export CARGO_BUILD_JOBS=2` for every cargo
  command (eight builders share 20 cores and 15 GB of RAM).

## What you produce

Under `release/capability-baseline/repair-1/<ws>/` (your handoff names `<ws>`):
1. `00-REPAIR-REPORT.md` — per class: requirement restated with source; what you changed (files, functions); the product
   check that now owns it and its tier; probes re-run with before/after lines; tests added/changed; limits and what you
   did **not** do; integration points; owner-decision questions if any.
2. `claims.yaml` — machine-readable: one entry per class `{class, status: REPAIRED_CLAIMED|NOT_REPAIRED|PARTIAL,
   files, product_checks, probes_rerun, integration_points, owner_decision_required}`.
3. `evidence/` — probe re-run outputs, regression outputs, R1 held-out re-run outputs where applicable.
4. Run report `release/orchestration/phase-2/AGENT_RUNS/<run-id>.report.yaml` (schema in `AGENT_RUNS/README.md`), verdict
   `READY_FOR_INDEPENDENT_CAPABILITY_VERIFICATION` (all assigned classes claimed), `OWNER_DECISION_REQUIRED` (a class
   stopped on a genuine owner question; the rest done), or `INCOMPLETE`.

Commit product changes and evidence on your branch (as many commits as useful), then write the run report naming your
final work commit in `output.commit`, and commit it. Do not merge, rebase onto other branches, tag or push. Do not touch
any other branch or worktree.

## Prohibitions

- No edits under `release/verification/`, `release/root-of-trust/`, `release/releases/`, `release/orchestration/phase-1/`,
  `release/capability-baseline/audit-0/`, or another workstream's `repair-1/` directory.
- Do not read, list or search session or agent transcripts, task-output stores (`/tmp/claude-*/**/tasks/` — including your
  own background command outputs: run long commands in the foreground, redirecting to a file in your evidence directory),
  or user auto-memory (`~/.claude/projects/**/memory/`). Write nothing there.
- Do not spawn sub-agents. Do not contact the product owner. Record your actual model identity in `agent_model`.
