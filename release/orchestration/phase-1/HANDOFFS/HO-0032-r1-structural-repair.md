# HO-0032 — Handoff for the authorised bounded R1 **structural** repair

| Field | Value |
|---|---|
| Handoff | HO-0032 |
| From | orchestrator (routing only) |
| To | fresh isolated R1 repair role — not AR-0028, not AR-0030 |
| Authorisation | `OWNER-DECISION-0008` (Option B), SHA-256 `aa541eab86192c3710a76cf3119efdeb7e108891c5f0e9782a88e05a20d06518` |
| Rejected candidate | `srr1-r1-candidate-3` (repair work `748c5d3`) |
| Verification | AR-0031, `BLOCKING_FINDINGS_PRESENT` (work commit `807a046`) |
| Active gate | `GATE-R1-CANDIDATE-ACCEPT` |
| R1 repair iteration | 3 (structural) |
| Required verdict | `READY_FOR_INDEPENDENT_OS_VERIFICATION` or `INCOMPLETE` |

## Independence

You did not author this implementation or either prior repair, and you do not grade your own repair. A NEW fresh
independent verifier re-verifies with its own held-out tests. All three prior held-out suites are committed and you may
read and run them — every one of those verdicts is issued.

## Why this repair is different

Three R1 iterations each closed the finding they were handed, and each time a new class surfaced underneath. The
product owner stopped the loop, read the root-cause package and authorised **one structural repair** to end the
pattern. You are that repair.

**The root cause, in one sentence:** `OWNER-DECISION-0006` §6 is a *universal negative* — "below-floor recovery MUST
NOT permit X" — and it has been implemented three times as a *positive enumeration* (forbidden operations → guarded
call sites → effect primitives), each complete when written and silently incomplete as soon as the product grew a path
its author had not enumerated. At every level the **test was derived from the same enumeration as the code**, so it
could not detect that the enumeration was short.

Fixing the two open blockers without addressing that would very likely produce a fourth iteration of the same shape.

## The owner's four-part mandate — all four are required

1. **Fix `AR31-B1`** (HIGH). §6 bullet 7 must be **enforced**, and the "every reporting surface carries the marking"
   claim must be **made true**.
2. **Fix `AR31-B2`** (MEDIUM). The enforcement points must fail **closed** when they cannot determine their subject.
3. **Remove the root cause.** §6 coverage must be **derived from the product** rather than relying on a manually
   asserted enumeration.
4. **Make "no primitive exists" falsifiable.** A bullet whose census entry asserts no primitive realises it must be
   **refutable by the product's own suite**.

## The two blockers in detail

### `AR31-B1` — HIGH — §6 bullet 7 is enforced nowhere

`Effect::PresentBelowFloorReleaseAsCurrent` has **no call site anywhere in the product** outside `breakglass.rs`
itself. Nothing is ever refused under bullet 7, so the whole bullet rests on the prose claim that every reporting
surface carries the marking — which is false:

- **`gov doctor`** — `doctor.rs` contains **zero** occurrences of `breakglass`, `is_degraded`, `Degraded` or
  `below_floor` (orchestrator-confirmed: `grep -c` = 0). A function holding no reference to the marking cannot emit it.
  Aggravating: `doctor`'s own vocabulary already uses `DEGRADED` for medium/low check failures, so the one word an
  operator scans for is taken.
- **`gov update --check`** — emits `{"current": <below-floor version>, "up_to_date": …, "recommendation": "nothing to
  do"}`. That is bullet 7 in the owner decision's own words. Read-only, so it never reaches `guard_write`.
- **`gov version`** and the **agent context packet** (`context/mod.rs`) — likewise carry no marking.

The three surfaces repair 2 did check do carry it; the ones it said it had not audited do not.

### `AR31-B2` — MEDIUM — both enforcement points fail open on an undetermined subject

`guard_effect` (`breakglass.rs:597-599`) and `guard_light` (`:355-360`) convert a `resolve_state_root()` error into a
clearance. **Repair 2's characterisation of this was wrong on both limbs**, and AR-0031 proved it:

- The unprovisioned case the code comment names **never reaches the branch** — `resolve_state_root` returns `Ok` for
  unprovisioned machines with or without an override. The only input that reaches it is
  `GOV_MACHINE_STATE_DIR` pointing elsewhere on a provisioned machine, which the product already refuses.
- The fail-open is **not** in machine-state path resolution and closing it does **not** touch
  `OWNER-DECISION-0007` §1. It is two `let … else { return Ok(…) }` blocks in `breakglass.rs` and nowhere else.
  `resolve_state_root`/`default_state_root` stay byte-identical under the fix.

Counterexample: on a provisioned, genuinely marked machine, one environment variable makes `guard_effect` return `Ok`
for **all eight** §6 effects and `guard_light` `Ok` for every label. Both points fail open together.
`set_root_metadata` is the exception that proves the diagnosis — `guard_effect_on` takes the `MachineState` and
resolves nothing, so bullet 4 holds.

No legitimate input reaches that branch, so failing closed costs nothing.

## The structural work — mandate parts 3 and 4

This is the part that ends the pattern. Two properties must become true:

- **Coverage is derived, not asserted.** The set of primitives that can realise each §6 effect must be obtained from
  the product itself, so that a newly added primitive appears in it without anyone remembering to add it. A hand-written
  list that happens to be correct today is exactly what failed three times.
- **A "no primitive exists" claim is falsifiable by the product's own suite.** Today it is not: `AR31-N5` shows the
  census test's loop **skips** the bullets whose entry says "no primitive", so bullets 6 and 7 cannot fail that test.
  That is precisely how `AR31-B1` survived repair 2. A bullet asserting no primitive must be the *most* tested case,
  not the least.

The shape is yours to choose — you know the codebase and the constraints better from inside it than this handoff can
prescribe. What matters is the property, not the mechanism. Say plainly in your report what your derivation can and
cannot see, and what would defeat it. An honest statement of the limits is worth more than an overclaim: three prior
roles overstated a universal property in this lineage and each overstatement was later falsified.

## Also in scope — residuals within the identified classes

`OWNER-DECISION-0008` authorises these to be repaired and re-verified automatically:

- **`AR31-N1`** — bullet 5's census entry is **false**: `tools::install` is a second primitive that never reaches the
  claimed sole sink. Non-blocking today only because the operation-level allow-list refuses `tools install` below
  floor. A derived census should surface this by construction.
- **`AR31-N2`** (INFO) — `guard_acquisition` asks §6 only `if is_privileged(descriptor)`, and `is_privileged` reads the
  descriptor: the only §6 sink whose decision to ask rests on self-asserted data.
- **`AR31-N3`** — the bullet-2 compiler guarantee is scoped to `gates.rs` because `build` is private;
  `records::new_record`/`save_record` and every `Record` field are `pub`, and AR-0031 minted a `human-gate` record
  **three ways with no `Clearance` in existence**. Either extend the guarantee or stop describing it as closing the class.
- **`AR31-N4`** — two held-out sub-checks were dropped in the `ho_f` migration: `f1`'s behavioural malleated-signature
  check and `f2`'s second half. Both properties still hold, but the malleability check now runs **nowhere** — and it
  cannot live in the product suite by design (`SRR-R0-L4`), which is why it belongs in held-out evidence. Restore the
  coverage somewhere durable.
- **`AR31-N5`** — the census test skipping "no primitive" bullets. This is mandate part 4.

## Explicitly OUT OF SCOPE

- **`AR27-OD1`** and machine-state path resolution — owner-closed by `OWNER-DECISION-0007` §1.
  `resolve_state_root`/`default_state_root` must stay byte-identical. Note `AR31-B2` does **not** require touching them.
- **`SRR2-R1-C1`** — the stricter both-floors exit is owner-decided policy. `exit_satisfied` and `EXIT_POLICY` stay as
  they are and it stays the single exit-floor comparison.
- **R2-lifecycle** `AR31-N6`, `AR29-N2`, `AR27-N3`, `N5`, `N6`, `N7` — carried, not this cycle.
- **`SRR-R0-L7`** — offline first install stays absent; break-glass recovery must still work with no network.

## Preservation — everything three verifiers confirmed must still hold

All twelve frozen R1 items (item 9 is qualified only by `AR31-B2`, which you are fixing). The four-operation §5
allow-list with exact-match semantics — AR-0029 could not break it across 63 near-miss forms and AR-0031 re-confirmed
it. Five `admit` sites paired with five `install_kernel` sites. Floors at all six ingresses, advancing last.
Transaction abort not a bypass. D-0007 a separate control establishing **intact**, never **authentic** or
**admissible**. `SRR-R0-L4` vacuous. `gov` verifies and never signs. `AuthenticatedRelease` sealed. Contract v3
canonical import byte-identical at `4c2df291…` and failing closed. Bullet 4's sink — the strongest in the set — intact.

Regression baseline at your base commit: `cargo test --lib` **36 passed**, `cargo test --test certification` **70
passed**, zero failures. No pre-existing test may be edited to make anything pass and no assertion weakened. Report
exact figures.

**Re-run all three prior held-out suites and report results**, editing none of them:
`release/verification/4.1.6-r1/evidence/heldout-tests/` (expect 26/3),
`release/verification/4.1.6-r1-2/evidence/heldout-tests/` (expect 26/2 with `ho_f` not compiling — that compile failure
is `AR29-N1` closing, not a regression), and `release/verification/4.1.6-r1-3/evidence/heldout-tests/` (its eight
`OBSERVED:` failures should flip toward passing as you close the findings; say which flip and which do not, and why).

## Hard prohibitions

No RoT-1 Revision 8; no CP-1 resumption; no D-0008/ARCH-0002 activation. Do not amend D-0007, D-0009, the accepted
ARCH-0003 body, the frozen boundary or any owner record. Do not modify `release/verification/**`,
`release/root-of-trust/*-review*/**`, `release/releases/**` or any historical record. No private keys. No R2 ceremony,
no R3 criteria. Do not read session/agent transcripts or task-output stores. Do not open or write user auto-memory. Do
not contact the product owner.

## Escalation rule — changed by the owner, read this

`OWNER-DECISION-0008` replaces the three-iteration rule for the remainder of R1:

- Residual defects **within** `BC-R1-1` (guard decision), `BC-R1-2` (guard coverage) and `BC-R1-3`
  (undetermined-subject fail-open) repair and re-verify **automatically**.
- **A genuinely new material blocker class, or anything needing an architecture or owner decision, escalates
  IMMEDIATELY — one occurrence, not three.**

So if you discover something that is neither one of the two blockers, nor a residual of those three classes, nor in
your authorised list — **stop and report it rather than fixing it**. Record it as `NEW_MATERIAL_CLASS_SUSPECTED` or
`NEW_OWNER_DECISION_REQUIRED` with your evidence. Reporting it is the correct action and costs nothing; quietly
absorbing it into this repair would hide exactly the signal the owner asked to see immediately.

Likewise, state plainly anything you suspect is unguarded or underivable but could not prove. Every prior role that did
this was right to, and it is how each class was found.

## Toolchain

`export PATH="$HOME/.cargo/bin:$PATH"` (cargo 1.98.1, not on PATH by default). Set `CARGO_TARGET_DIR` into scratch.

## Deliverables

- The repair, committed on branch `phase1/srr1-r1-repair-3`.
- Evidence under `release/root-of-trust/signed-release-root-v1-r1-repair-3/`: what changed per finding; **the
  derivation mechanism, what it can and cannot see, and what would defeat it**; how a "no primitive exists" claim can
  now fail; the full regression output; all three prior held-out suite results; and `REVIEWED-CONTENT-DIGESTS.txt`.
- `release/orchestration/phase-1/AGENT_RUNS/AR-0032.report.yaml` per the `AGENT_RUNS/README.md` schema, committed after
  the work commit and naming it in `output.commit`.

An honest `INCOMPLETE` is better than a false readiness claim. You declare readiness only; never acceptance.
