# HO-0033 — Handoff for the fresh independent R1 verification of candidate 4

| Field | Value |
|---|---|
| Handoff | HO-0033 |
| From | orchestrator (routing only) |
| To | NEW fresh independent R1 verifier — **not** AR-0027, AR-0029, AR-0031, and not either repair role |
| Candidate | `srr1-r1-candidate-4` (structural repair work commit `cf52741`) |
| Repair run | AR-0032 `READY_FOR_INDEPENDENT_OS_VERIFICATION`, structural repair under `OWNER-DECISION-0008` |
| Active gate | `GATE-R1-CANDIDATE-ACCEPT` |
| R1 verification iteration | 4 |
| Required verdict | `ROT_PHASE1_CANDIDATE_ACCEPTED_R1` or `BLOCKING_FINDINGS_PRESENT` |

## Independence

You authored none of this — not the implementation, none of the three repairs, none of the three prior verifications.
You author your own held-out tests. You are the sole issuer of this verdict, and the orchestrator will not overrule it.

## What changed and why this iteration is different

Three R1 iterations each closed the finding they were handed and each surfaced a new class underneath. The product
owner stopped the loop, read the root-cause analysis and authorised **one structural repair** with a four-part mandate:
fix `AR31-B1` and `AR31-B2`, **derive §6 coverage from the product** rather than a manually asserted enumeration, and
make any **"no primitive exists" claim falsifiable** by the product's own suite.

AR-0032 claims all four are met. **Your job is to find out whether the derivation actually holds** — it is the thing
that is supposed to stop a fifth iteration of the same shape, and it is therefore what deserves your hardest work.

## Primary target: attack the derivation itself

`SECTION_6_SIGNATURES` in `breakglass.rs` names, per §6 bullet, the product primitives an implementation of that effect
must use. `section_6_coverage_is_derived_from_the_product` walks every function in `runtime/src` and `cli/src` — a
claimed 84 files and 740 functions — and for each effect derives every function that performs a durable write (itself
derived from `SECTION_6_WRITE_PRIMITIVES`) and matches the signature. Each must carry the enforcement or call the sink.
Claimed result: **0 violations, 1 recorded exemption** (`cit::take_snapshot`).

Three questions, in the repair's own words, that it asked you to attack:

1. **Can `SECTION_6_SIGNATURES` be made to miss a primitive a plausible future author would write?** Write that author's
   code and see.
2. **Does any acceptance marker accept something unenforced?** The repair flags this as *"as load-bearing as signatures
   and less defended — widening one to something common would accept everything silently"*, and says it could not find a
   cheap fix.
3. **Does the bullet-7 marking survive a reporting path that does not go through the CLI envelope?** Bullet 7's
   universality is claimed as a property of the **CLI boundary**, not the library.

The repair documents **nine limits** in `evidence/DERIVATION.md` §4 and **five defeat conditions** in §5. Read both
sections and test them rather than accepting them. Specifically: it is syntactic, not a decision procedure; an
implementation using none of the product's primitives (hand-built path + `std::fs::write`) is invisible; anything
outside those two trees or after a `#[cfg(test)]` line is unseen; it assumes rustfmt formatting; acceptance is by marker,
not reachability; a `&Clearance` is trusted at the boundary.

**Judge the exemption.** `cit::take_snapshot` is the single recorded exemption and the repair says plainly it is *"the
one place a wrong judgement passes quietly — a verifier should read it"*. Read it.

## The falsifiability claim (mandate part 4)

Each effect's detector is claimed to run first against a **positive control** — a synthetic unguarded implementation
that it must flag — and to fail the suite if it cannot flag its own control; to not fire on arithmetic; to **panic**
rather than pass silently when a signature derives nothing; and `a_no_primitive_claim_is_refutable_by_this_suite` is
claimed to fail outright on any `"no primitive"` entry. `AR31-N5` was exactly the opposite property. **Verify that the
positive controls are genuine** — a control that is trivially flaggable proves nothing, and a detector tuned to its own
control is the same failure one level along.

## Bullet 7 (`AR31-B1`)

New `runtime/src/srr/present.rs` is the sink: `presentation()` asks `guard_effect(Effect::PresentBelowFloorReleaseAsCurrent, …)`
and **the answer is the presentation** — refused becomes the marking, entry time, exit condition, and a demotion of any
affirmative currency claim. It is infallible by design, because §5 requires inspection to stay available below floor, so
§6 is enforced in *what is said*. The effect had zero call sites in the product; it now has five. `update --check` is
claimed to report `up_to_date: false` with the exit condition instead of "nothing to do", and the marking is claimed to
**lift** on an unmarked machine (`CURRENT`, `marking: null`).

Test both directions — a below-floor machine must not read as current, and an unmarked machine must not be spuriously
marked. Then test the CLI-boundary claim: the repair says `run(&cli)` is called once and its value reaches stdout
through one envelope. Find a path that does not.

## `AR31-B2`

Both `let … else { return Ok(…) }` blocks now route to `undetermined_subject` → `SRR_BELOW_FLOOR_SUBJECT_UNDETERMINED`,
`"fail": "closed"`, with the allow-list consulted first so no §5 route is blocked. Verify the fail-closed behaviour and
that §5 restoration still works — a recovery mode you cannot exit would be a new defect.

## Two items the derivation found by itself

The repair reports these were surfaced by the mechanism rather than handed to it, and closed: **`Floors`' `pub` fields
and `pub save` were a floor-lowering primitive** — `Floors::save` is now bullet 6's sink, monotonic against the
persisted value; and **CIT `write_file`/`move_file` reached a governed record path without `save_record`**. Both sit
inside `BC-R1-2`. Verify both closures, and treat the fact that the mechanism found them as evidence for or against the
derivation working — you decide which.

Also: **`gov gate present` reaches no `guard_write`**, so it previously mutated a Human Gate record below floor and is
now refused at the record-write sink. That is a behaviour change worth confirming.

## Residual dispositions to check

`AR31-N1` (`tools::install` → `guard_acquisition_below_floor`; the derived census is claimed to find both registry
writers), `AR31-N2` (`guard_acquisition` now asks §6 unconditionally — the descriptor no longer decides whether the
question is put), `AR31-N3` (`records::save_record` is the record-write sink keyed by record type, claimed to refuse all
three of AR-0031's constructions; `gates::build`'s `&Clearance` kept), `AR31-N4` (the malleated-signature and
relaxation-switch checks restored in `tests/certification/section6.rs`), `AR31-N5` (mandate part 4).

For `AR31-N4`, note the property AR-0031 identified: the malleability check **cannot** live in the product suite by
design under `SRR-R0-L4`. Judge whether its restoration in `section6.rs` genuinely preserves the property or whether it
has been weakened by the move — this is the second time a check has migrated into the implementer's own suite.

## Prior held-out suites — rerun all three, edit none

Committed byte-identical (orchestrator-verified unchanged at this commit). The repair reports:

- **AR-0027: 26/3** — unchanged.
- **AR-0029: 26/2 of 28 compiled, `ho_f` not compiling** — unchanged; that compile failure is `AR29-N1` closing.
- **AR-0031: 27/7** (from 26/8). Four flipped to passing; **three flipped to failing** — all claimed to be structural
  tripwires asserting the *old* shape, where the failure *is* the repair (`hx_a::a1`, `hx_b::b6`, `hx_d::d2`); four
  still failing, three of which are claimed to fail at a *location* assertion because they grep
  `tests/certification/srr.rs`, which the repair deliberately did not edit, with the properties closed in the product
  and tested in `section6.rs`.

**Verify that account rather than accepting it.** A repair explaining why a verifier's test now fails is exactly where a
real regression can hide behind a plausible story. For each of the seven failures decide independently: is the property
still held, and is it still tested somewhere durable?

## Owner-closed — verify but do not grade

`OWNER-DECISION-0007`: `AR27-OD1` (machine state from `XDG_STATE_HOME`/`HOME`) and `SRR2-R1-C1` (stricter both-floors
exit). The orchestrator confirmed `resolve_state_root`, `default_state_root` and `exit_satisfied` byte-identical and
`EXIT_POLICY` unchanged despite `state.rs` and `breakglass.rs` both being edited — confirm independently, do not grade.
`SRR-R0-L7`: offline first install absent; break-glass recovery works with no network.

## Preservation — must still hold

All twelve frozen R1 items. The four-operation §5 allow-list with exact-match semantics. Five `admit` sites paired with
five `install_kernel` sites; one `by_admit`; one `AuthenticatedRelease` literal; zero `Clearance` constructions outside
`breakglass`. Floors at all six ingresses, advancing last. Transaction abort not a bypass. D-0007 a separate control
establishing **intact**, never **authentic** or **admissible**. `SRR-R0-L4` vacuous. `gov` verifies and never signs.
Contract v3 canonical import byte-identical at `4c2df291…` and failing closed.

Regression: the repair reports `cargo test --lib` **42 passed** (36 + 6) and `cargo test --test certification` **79
passed** (70 + 9), zero failures, with `tests/certification/srr.rs` untouched. The orchestrator independently
reproduced these figures. Reproduce and report your own.

## Classification, routing and the owner's escalation rule

Every finding states: exact normative source; provenance class; lifecycle/gate; whether it falsifies a claim or
proposes stronger assurance; consequence; evidence or a bounded counterexample; and **residual-versus-materially-new**.

A finding blocks R1 only if its normative source and lifecycle are R1, or it falsifies an R1 claim. Do not promote
R2/R3 material into R1 blockers. Mark `REQUIRES_R0_OR_OWNER_ADJUDICATION` on anything that would change the accepted R0
boundary or an owner-decided trade-off.

**`OWNER-DECISION-0008` changed the convergence rule.** Residuals within the three known classes — `BC-R1-1` guard
decision, `BC-R1-2` guard coverage, `BC-R1-3` undetermined-subject fail-open — are repaired and re-verified
automatically. **A genuinely new material blocker class, or anything needing an architecture or owner decision, stops
the loop and escalates to the owner immediately — one occurrence, not three.** So your residual-versus-new label now
directly determines whether the owner is interrupted. Label precisely and say why. Do not shade a new class into a
residual to let the phase finish, and do not inflate a residual into a new class.

## Prohibitions

Do not modify product source, the frozen boundary, owner records, prior review or verification evidence,
`release/releases/**`, or any historical record — your own new evidence directory is the sole exception. Do not
implement fixes. Do not read session/agent transcripts or task-output stores. Do not open or write user auto-memory. Do
not contact the product owner. Disclose any delegation.

Judge honestly. An accurate acceptance, an accurate rejection and an accurate escalation are all good outcomes; only an
inaccurate verdict or an inaccurate classification is a failure.

## Toolchain

`export PATH="$HOME/.cargo/bin:$PATH"` (cargo 1.98.1, not on PATH by default). Set `CARGO_TARGET_DIR` into scratch.

## Deliverables

Evidence under `release/verification/4.1.6-r1-4/`: `00-VERIFICATION-REPORT.md` (item-by-item disposition of the frozen
R1 section, your attack on the derivation, each of the nine limits and five defeat conditions, the exemption, the
falsifiability controls, bullet 7 in both directions, and every one of the seven AR-0031 failures),
`10-BLOCKING-FINDINGS.md` (present and explicitly empty if none), `20-LATER-LIFECYCLE-CONDITIONS.md`, and `evidence/`
with your held-out test sources and output, all three prior suites' rerun output, `REVIEWED-CONTENT-DIGESTS.txt` and
reproduction instructions.

Commit that, then write `release/orchestration/phase-1/AGENT_RUNS/AR-0033.report.yaml` per the `AGENT_RUNS/README.md`
schema with `output.commit` naming the work commit, and commit it separately. A run without a durable committed report
is INCOMPLETE and advances no gate.
