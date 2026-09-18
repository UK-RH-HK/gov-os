# HO-0031 — Handoff for the fresh independent R1 re-verification (candidate 3)

| Field | Value |
|---|---|
| Handoff | HO-0031 |
| From | orchestrator (routing only) |
| To | NEW fresh independent R1 verifier — **not** AR-0027, **not** AR-0029, **not** AR-0028/AR-0030 |
| Candidate | `srr1-r1-candidate-3` (repair work commit `748c5d3`) |
| Prior verdicts | AR-0027 rejected candidate 1; AR-0029 rejected candidate 2 |
| Repair run | AR-0030 `READY_FOR_INDEPENDENT_OS_VERIFICATION`, repair cycle 2 |
| Active gate | `GATE-R1-CANDIDATE-ACCEPT` |
| R1 verification iteration | 3 |
| Required verdict | `ROT_PHASE1_CANDIDATE_ACCEPTED_R1` or `BLOCKING_FINDINGS_PRESENT` |

## Independence

You authored none of this — not the implementation, either repair, either prior verification, nor the architecture.
You author your own held-out tests. You are the sole issuer of this verdict.

## Convergence context — why your classification matters more than usual

Two R1 iterations have each closed their assigned findings completely and then surfaced a **materially new blocker
class** one level deeper:

- **Iteration 1** (AR-0027): `AR27-B1` — the guard's *decision* was a substring deny-list rather than a class control.
- **Iteration 2** (AR-0029): `AR29-B1`/`B2` — *coverage*: privileged operations that reached no guard at all.

The orchestrator has committed to **stopping the phase with `PHASE_CONVERGENCE_ESCALATION_REQUIRED` and producing a
root-cause package for the product owner if this iteration produces a third materially new class.**

So: for every blocking finding, state explicitly whether it is a **residual** of a named prior finding or a
**materially new class**, and say why. Do not shade a genuinely new class into "residual" to keep the phase alive, and
do not inflate a residual into a new class. An accurate acceptance, an accurate rejection and an accurate escalation
are all good outcomes; only an inaccurate classification is a failure.

## What repair 2 claims — and where it says it is weakest

The repair turns on a distinction: **§6 bullet 1 names a class of *operations*; bullets 2–7 name *effects*.**
`gov trust root-update` takes no `Project`, so it can never reach the operation chokepoint. `update --apply` is an
*allow-listed operation* that *contains* a bullet-2 effect. Guarding operations misses both.

So a second enforcement point was added **inside the single primitive that realises each effect**, not beside the
callers — `breakglass::Effect`, `guard_effect`/`guard_effect_on` → `Clearance`, with `breakglass::SECTION_6_SINKS` as
a machine-readable census:

| bullet | claimed sole sink | enforcement |
|---|---|---|
| 2 create | `gates::build` (only constructor of a `human-gate` record) | compiler — takes `&Clearance` |
| 2 approve | `gates::answer` | `guard_effect` |
| 3 | `release::build` | `guard_effect` |
| 4 | `MachineState::set_root_metadata` (only writer of `trust/root.json`) | `guard_effect_on` |
| 5 | `srr::plugins::guard_acquisition` | `guard_effect` |
| 6, 7 | **no primitive claimed to exist** | asserted, not assumed |

**Attack the census itself.** The whole class control rests on "exactly one primitive realises each effect, and the
check is inside it". Your highest-value work is deciding whether `SECTION_6_SINKS` really enumerates **every**
primitive that can realise each bullet — and whether a second path to any of those effects exists that the census does
not name. The repair explicitly recommends you go after this joint.

**Four things the repair itself flags as unproven or weaker — judge each independently:**

1. **`guard_effect` fails open when `resolve_state_root()` errors**, exactly as `guard_light` has since repair 1. The
   repair calls this inherited, not introduced, and says fixing it would mean changing machine-state root resolution,
   which `OWNER-DECISION-0007` §1 puts out of scope. **Test whether that characterisation is right.** If a §6 check can
   be skipped without a code change, decide honestly whether that is R1-blocking, and whether closing it truly requires
   the owner-closed change (if it does, mark it `REQUIRES_R0_OR_OWNER_ADJUDICATION` rather than repairing it).
2. **§6 bullet 7** ("treating the below-floor release as current or fully trusted") has no sink because it is claimed
   no primitive exists. The repair verified `gov trust status`, `gov trust break-glass` and `gov recover`, but did
   **not** exhaustively audit `gov status`, `gov doctor` or telemetry for a field readable as "current and fully
   trusted" without the marking beside it. It believes it holds; it did not prove it. **Prove or falsify it.**
3. **§6 bullet 5's sink is the acquisition *decision*, not a byte-installing primitive.** `plugins::guard_acquisition`
   has one caller; `tools::install` reaches the effect through the operation-level guard only. The repair calls this
   genuinely weaker than the bullet 2 and 4 sinks. Judge whether that is sufficient for R1.
4. **`Clearance` is a witness, not a lifetime-scoped capability**, and is deliberately *not* used for
   `set_root_metadata`/`release::build`/`guard_acquisition` — the repair's reasoning is that a token handed in by a
   caller is a decision taken earlier, while those sinks ask at the instant of the effect. It states the trade so you
   can disagree with it explicitly. Do.

## Three changes to prior evidence you must handle correctly

These are consequences of the repair, not regressions — but verify that for yourself rather than taking it on trust:

1. **AR-0029's `ho_f_preservation` no longer compiles**: `cannot construct AuthenticatedRelease with struct literal
   syntax due to private fields`. Its `f4` *is* the literal that `AR29-N1` asked to be made impossible, so the compile
   error is the finding closing. The repair reproduced `ho_f`'s six unrelated preservation checks in the product suite
   as `the_no_bypass_and_no_signing_preservation_census_still_holds` rather than losing them. **Confirm those six
   checks are genuinely reproduced and not weakened in the move** — that is a real risk when a test migrates from an
   independent crate into the suite the implementer controls.
2. **AR-0029's `ho_b::b3` and `::b6` flipped from passing to failing.** Both assert the *absence* of a guard and carry
   re-derive-this-census messages ("root_update unexpectedly guards", "a guard now sits between the allow-list entry
   and the gate creation"). Both new statements are the repair working. **`b3`'s printed §6 census is now stale —
   re-derive it yourself rather than treating the flip as a regression.**
3. **`ho_b::b4` was briefly broken and the repair reverted the cause.** Putting the §6 guard before `provision`'s
   already-provisioned check turned `SRR_ALREADY_PROVISIONED` into `SRR_BELOW_FLOOR_REFUSED`, a property AR-0029 had
   verified as satisfied. The guard now sits after that check and §6 at that door is proved at the sink instead.
   **Verify both: that `b4` passes again, and that the door is genuinely closed at the sink.**

Both prior held-out suites are committed byte-identical (orchestrator-verified unchanged at this commit) and you must
not edit either. Rerun them. Expect AR-0027 at 26/3 (its three `OBSERVED` flips) and AR-0029's four `OBSERVED:`
failures flipped to passing, with `ho_b` at 4/2 and `ho_f` not compiling as described.

## Owner-closed — verify but do not grade

`OWNER-DECISION-0007`: **`AR27-OD1`** (machine-state derived from `XDG_STATE_HOME`/`HOME`) and **`SRR2-R1-C1`** (the
stricter both-floors exit) are both closed by owner decision. Confirm `resolve_state_root`/`default_state_root` are
untouched and `exit_satisfied`/`EXIT_POLICY` are unchanged and still the single exit-floor comparison — the orchestrator
verified all of this, and you should confirm it — but do **not** grade either policy.

`SRR-R0-L7`: offline first install stays absent; break-glass recovery must still work with no network.

## Carried, not this cycle

R2-lifecycle `AR29-N2`, `AR27-N3`, `N5`, `N6`, `N7`. Do not raise them as R1 blockers.

## Preservation — must still hold

All twelve frozen R1 items. The four-operation §5 allow-list and its exact-match semantics (`AR27-B1`'s closure, which
AR-0029 could not break across 63 near-miss forms). Five `admit` sites paired with five `install_kernel` sites. Floors
at all six ingresses, advancing last. Transaction abort still not a bypass. D-0007 a separate control establishing
**intact**, never **authentic** or **admissible**. `SRR-R0-L4` vacuous. `gov` verifies and never signs. Contract v3
canonical import byte-identical at `4c2df291…` and failing closed.

Regression: the repair reports `cargo test --lib` **36 passed** (31 + 5 new) and `cargo test --test certification`
**70 passed** (65 + 5 new), zero failures, `tests/certification/srr.rs` at +866/−0 purely additive. The orchestrator
independently reproduced these figures. Reproduce and report your own.

## Classification and routing

Every finding states: exact normative source; provenance class; lifecycle/gate; whether it falsifies a claim or
proposes stronger assurance; consequence; evidence or a bounded counterexample; and **residual-versus-materially-new**.

A finding blocks R1 only if its normative source and lifecycle are R1, or it falsifies an R1 claim. Do not promote
R2/R3 material into R1 blockers. Mark `REQUIRES_R0_OR_OWNER_ADJUDICATION` on anything that would change the accepted R0
boundary or an owner-decided trade-off.

## Prohibitions

Do not modify product source, the frozen boundary, owner records, prior review or verification evidence,
`release/releases/**`, or any historical record — your own new evidence directory is the sole exception. Do not
implement fixes. Do not read session/agent transcripts or task-output stores. Do not open or write user auto-memory. Do
not contact the product owner. Disclose any delegation.

## Toolchain

`export PATH="$HOME/.cargo/bin:$PATH"` (cargo 1.98.1, not on PATH by default). Set `CARGO_TARGET_DIR` into scratch.

## Deliverables

Evidence under `release/verification/4.1.6-r1-3/`: `00-VERIFICATION-REPORT.md`, `10-BLOCKING-FINDINGS.md` (present and
explicitly empty if none), `20-LATER-LIFECYCLE-CONDITIONS.md`, `evidence/` with your held-out test sources and output,
both prior suites' rerun output, `REVIEWED-CONTENT-DIGESTS.txt` and reproduction instructions.

Commit that, then write `release/orchestration/phase-1/AGENT_RUNS/AR-0031.report.yaml` per the `AGENT_RUNS/README.md`
schema with `output.commit` naming the work commit, and commit it separately. A run without a durable committed report
is INCOMPLETE and advances no gate.
