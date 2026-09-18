# HO-0030 — Handoff for bounded R1 repair 2

| Field | Value |
|---|---|
| Handoff | HO-0030 |
| From | orchestrator (routing only) |
| To | fresh isolated R1 repair role (not AR-0028) |
| Base commit | `1bc4427d0f9ceba0da23892d5897cdfc863e2cee` |
| Rejected candidate | `srr1-r1-candidate-2` (repair work `4c7c40c`) |
| Verification | AR-0029, `BLOCKING_FINDINGS_PRESENT` (work commit `d3f52c6`) |
| Active gate | `GATE-R1-CANDIDATE-ACCEPT` |
| R1 repair iteration | 2 |
| Required verdict | `READY_FOR_INDEPENDENT_OS_VERIFICATION` or `INCOMPLETE` |

## Independence

You are not AR-0028 and you do not grade your own repair. A NEW fresh independent verifier re-verifies with its own
held-out tests. AR-0027's and AR-0029's held-out tests are committed and you may read and run them — both verdicts are
issued.

## What repair 1 got right — preserve it

Repair 1 closed `AR27-B1` **structurally** and AR-0029 confirmed it could not be broken: exact match held against 63
near-miss forms with zero permitted, refusal is genuinely the default, `REFUSAL_CLASSES` is inert, and a 28-label sweep
through the real guard permits exactly four §5 operations. `AR27-N1`, `N2` and `N4` are closed. **Do not disturb any of
this.** The allow-list shape, `permitted_activity`, `REFUSAL_POLICY`, the expiry canonical-form gate,
`ROOT_EXPIRY_PROFILE` and `crypto::verify` being strict-only must all survive unchanged in behaviour.

## The finding class you must close

AR-0029 asked the prior question: **is the guard on the path at all?** For two §6 bullets it is not. A perfect decision
procedure at a chokepoint enforces nothing for an operation that never passes through it.

### `AR29-B1` — MEDIUM — trust-policy mutation completes below floor (§6 bullet 4)

`provision::root_update` calls neither `control::guard_write` nor `breakglass::guard`. Measured end to end on a machine
marked `DEGRADED — RECOVERY ONLY`: `gov trust root-update` returned `Ok(true)`, the anchor advanced 1 → 2, a key was
revoked, the metadata high-water advanced, and the machine stayed degraded. The guard **would** refuse it —
`permitted_activity("trust root-update")` is `None` and `REFUSAL_CLASSES` even maps that exact label to
`trust_policy_mutation` — but nothing asks the guard.

### `AR29-B2` — MEDIUM — new Human Gates are created below floor (§6 bullet 2)

`orchestration::gates::create_system` (line 143) saves a `human-gate` record and blocks tasks with **no guard**, unlike
its guarded sibling `gates::create` (line 132, which calls `control::guard_write(p, "gate create")`). Two reachable
callers below floor: `kernel_trust::request_override`, and — more awkwardly — `update::apply_update_opts` at
`update.rs:157`, i.e. **inside the allow-listed `update --apply`**, with nothing between the `Ok` guard result and the
gate creation.

### The shape of the fix

Do **not** bolt a guard call onto `root_update` and `create_system` one at a time. That closes two instances and leaves
the class open — exactly the mistake `AR27-B1` taught one level down.

Build **a single enforcement point that every trust-changing and gate-creating path must pass**, so that an operation
added to the product tomorrow inherits §6 by construction rather than by someone remembering. Then add a **coverage
test that enumerates the paths** and fails when a new one appears unguarded — a test that would have caught both of
these. Make the mechanism, not the list, the thing that holds.

`OWNER-DECISION-0006` §6 already decides the policy. You are implementing a decided policy; no owner decision is
required and none may be invented.

Where an allow-listed operation legitimately needs an internal step that §6 forbids — `update --apply` creating a
Human Gate is the live case — resolve it honestly: either the operation cannot complete below floor and the allow-list
must say so, or the internal step is genuinely part of the §5 activity and the enforcement point must express that.
Do not leave the allow-list and the reachable behaviour disagreeing (see `AR29-N4`).

## Also in scope this cycle

- **`AR29-C1`** (LOW, residual of `AR27-B1`) — the unreadable-marking **exit** path. Restoration stays open under an
  unreadable marking, but `try_exit` goes through `Degraded::load`, which reads the same record with the opposite
  disposition (returns `None`, writes nothing). After installing an authenticated release above both floors — the exact
  `OWNER-DECISION-0007` §2 exit condition — the guard still refuses, while `gov trust status` reports `degraded: null`
  and `gov trust break-glass` reports `currently_degraded: false`. **Two readers of one record disagree.** Make them
  agree.
- **`AR29-N3`** (INFO) — `guard_light` and `degraded_path` use two different path sanitisers. Identical for the
  current `FRAMEWORK_NAME`, but a latent silent §6 bypass for any other product string. Unify them.
- **`AR29-N4`** (LOW) — `update --apply` is nominally permitted but cannot complete below floor when a gate is
  required. Not a deadlock (`kernel reinstall` and `update --rollback` are gate-free), but the allow-list and the
  reachable behaviour must be made to agree.
- **`AR29-N5`** (INFO) — `REFUSAL_CLASSES` names 8 operations that do not exist in the product. That is the mechanism
  behind AR-0027's false negative: refusing a *label* proved nothing about an *operation*. Remove the phantoms or make
  them verifiable.
- **`AR29-N1`** (INFO, but fix it) — "constructible only by `admit`" is an **enumeration property, not a type
  property**: every field of `AuthenticatedRelease`, `Staged`, `MachineState` and `Floors` is `pub`, so a struct
  literal outside the module compiles and runs — AR-0029's test is one. The 5/5 call-site census is what actually
  holds. Either make the claim true by sealing the constructors (private fields plus a constructor only `admit` can
  reach), or correct every place that overstates it. **Sealing is preferred** — this property has been reported upward
  as compiler-enforced and should become so.

## Explicitly OUT OF SCOPE

- **`AR27-OD1`** and machine-state path resolution — owner-closed by `OWNER-DECISION-0007`. `runtime/src/srr/state.rs`
  path resolution must not change.
- **`SRR2-R1-C1`** — the stricter both-floors exit is owner-decided policy. `breakglass::exit_satisfied` and
  `EXIT_POLICY` stay as they are, and it stays the single exit-floor comparison. `AR29-C1` is about the marking being
  *readable*, not about the exit *policy* — do not widen the policy point.
- **R2-lifecycle** `AR29-N2`, `AR27-N3`, `N5`, `N6`, `N7` — carried, not this cycle.
- **`SRR-R0-L7`** — offline first install stays absent; break-glass recovery must still work with no network.

## Preservation — must still hold

Everything AR-0029 found satisfied: all twelve frozen R1 items; the four-operation allow-list and its exact-match
semantics; five `admit` sites paired with five `install_kernel` sites; floors at all six ingresses and advancing last;
transaction abort still not a bypass; D-0007 a separate control establishing **intact**, never **authentic** or
**admissible**; `SRR-R0-L4` vacuous; `gov` verifies and never signs; Contract v3 canonical import byte-identical at
`4c2df291…` and failing closed.

Regression baseline at your base commit: `cargo test --lib` **31 passed**, `cargo test --test certification` **65
passed**, zero failures. No pre-existing test may be edited to make anything pass and no assertion weakened. Report
exact figures.

**Re-run both prior held-out suites** and report results: AR-0027's at
`release/verification/4.1.6-r1/evidence/heldout-tests/` (expect 26/3, the three being its own `OBSERVED` flips) and
AR-0029's at `release/verification/4.1.6-r1-2/evidence/heldout-tests/` (expect its four `OBSERVED:` failures to flip to
passing once you close the findings). Do not edit either suite.

## Hard prohibitions

No RoT-1 Revision 8; no CP-1 resumption; no D-0008/ARCH-0002 activation. Do not amend D-0007, D-0009, the accepted
ARCH-0003 body, the frozen boundary or any owner record. Do not modify `release/verification/**`,
`release/root-of-trust/*-review*/**`, `release/releases/**` or any historical record. No private keys. No R2 ceremony,
no R3 criteria. Do not read session/agent transcripts or task-output stores. Do not open or write user auto-memory. Do
not contact the product owner — record any `NEW_OWNER_DECISION_REQUIRED` item in your report.

## Convergence note — read this

This is R1 repair iteration 2. Iteration 1 closed everything it was given, and verification then found a materially new
class one level deeper. **If a third iteration produces another materially new blocker class, the orchestrator stops
the phase and produces a root-cause package for the product owner.** That is not a reason to rush or to paper over
anything — it is a reason to fix the *class* properly rather than the two instances, and to say plainly in your report
anything you suspect is unguarded but did not have time to prove.

## Toolchain

`export PATH="$HOME/.cargo/bin:$PATH"` (cargo 1.98.1, not on PATH by default). Set `CARGO_TARGET_DIR` into scratch.

## Deliverables

- The repair, committed on branch `phase1/srr1-r1-repair-2`.
- Evidence under `release/root-of-trust/signed-release-root-v1-r1-repair-2/`: what changed and why per finding; the
  enforcement-point design and why it closes the class rather than the instances; the coverage test and what it would
  have caught; the full regression output; both prior held-out suite results; and `REVIEWED-CONTENT-DIGESTS.txt`.
- `release/orchestration/phase-1/AGENT_RUNS/AR-0030.report.yaml` per the `AGENT_RUNS/README.md` schema, committed after
  the work commit and naming it in `output.commit`.

An honest `INCOMPLETE` is better than a false readiness claim. You declare readiness only; never acceptance.
