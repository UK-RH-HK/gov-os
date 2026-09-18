# AR-0030 — bounded R1 repair 2 of `srr1-r1-candidate-2`

| Field | Value |
|---|---|
| Run | AR-0030, fresh isolated R1 repair role, repair cycle 2. **Not AR-0028.** |
| Handoff | `release/orchestration/phase-1/HANDOFFS/HO-0030-r1-repair-2.md` |
| Branch / worktree HEAD at start | `phase1/srr1-r1-repair-2` @ `f5717a9d92419f7588889e0ce5aa96bf641e3fb2` |
| Repairs | `AR29-B1`, `AR29-B2` (blocking) and `AR29-C1`, `AR29-N1`, `AR29-N3`, `AR29-N4`, `AR29-N5` |
| Verdict | **`READY_FOR_INDEPENDENT_OS_VERIFICATION`** — a readiness declaration only, never an acceptance |
| Graded by | a NEW fresh independent verifier, with its own held-out tests. Not by this run. |

Files changed — all of them, nothing else:

```
runtime/src/orchestration/gates.rs    38 +    3 -
runtime/src/release.rs                11 +    0 -
runtime/src/srr/breakglass.rs        527 +   59 -
runtime/src/srr/plugins.rs            10 +    0 -
runtime/src/srr/provision.rs          16 +    0 -
runtime/src/srr/state.rs              38 +    3 -
runtime/src/srr/verifier.rs           45 +    4 -
runtime/src/update.rs                 11 +    0 -
tests/certification/srr.rs           866 +    0 -      (purely additive: no pre-existing test touched)
```

---

## 1. The class, and why the two instances are not the fix

`AR29-B1` and `AR29-B2` are one finding twice. Repair 1's decision procedure is correct — AR-0029 could not break
it against 63 near-miss forms — and neither operation ever asked it. `provision::root_update` calls no guard;
`gates::create_system` calls no guard. Bolting a guard call onto each closes two instances and leaves the class
open, because the next trust-changing or gate-creating function will need someone to remember. That is the same
mistake `AR27-B1` taught one level up: an enumeration standing in for a property.

The property that has to hold is not "these operations are guarded". It is:

> **No §6-forbidden effect can happen below floor, whatever code path reaches it, including code that has not been
> written yet.**

### The distinction the repair turns on: §6 names effects, not operations

`OWNER-DECISION-0006` §6 bullet 1 names a **class of operations** — "normal privileged Governance OS operation".
Bullets 2–7 name **effects**: creating or approving a Human Gate, certifying a release, mutating trust policy,
acquiring a privileged plugin, lowering a floor, presenting a below-floor release as current.

An effect is not an operation, and the two instances show it from both sides:

* `gov trust root-update` is an *operation* that takes no `Project`, so it can never reach
  `control::guard_write`. Guarding "operations that pass the chokepoint" misses it by construction.
* `update --apply` is an *allow-listed* operation that contains a §6 bullet 2 effect. Guarding the operation
  permits it — correctly, it is §5 restoration — and the effect inside it goes unexamined.

So the repair adds a second enforcement point at the level §6 actually legislates, and puts it **inside the
effect**.

### The enforcement point

`runtime/src/srr/breakglass.rs`:

```rust
pub enum Effect { NormalPrivilegedOperation, HumanGateCreate, HumanGateApprove,
                  ReleaseCertification, TrustPolicyMutation, PrivilegedPluginAcquisition,
                  FloorLowerOrReset, PresentBelowFloorReleaseAsCurrent }   // one per §6 bullet

pub fn guard_effect_on(ms, product, effect, operation) -> Result<Clearance>   // state-carrying
pub fn guard_effect(effect, operation)               -> Result<Clearance>     // resolves the state root
```

Three properties make it a class control:

1. **It is called from inside the primitive that performs the effect, not beside the callers.** A caller that does
   not exist yet still reaches the effect only through its primitive, and the primitive refuses. Enforcement is a
   property of the effect.
2. **There is no allow-list exception.** `PERMITTED_OPERATIONS` is the §5 exception to bullet 1 *and to bullet 1
   only*. Bullets 2–7 bind inside a permitted operation exactly as they bind outside one.
3. **It is one decision.** `guard`, `guard_light` and `guard_effect*` all end in one private `decide`, over one
   reading of the record (`read_marking`), through one `refuse`. Nothing can drift.

### The sinks — `breakglass::SECTION_6_SINKS`

For each bullet, the single primitive in the product that can realise the effect:

| §6 bullet | effect | sink | how it is enforced |
|---|---|---|---|
| 1 normal privileged operation | — | `orchestration::control::guard_write` → `breakglass::guard_light` | unchanged from repair 1 |
| 2 Human Gate **creation** | `HumanGateCreate` | `orchestration::gates::build` — the only constructor of a `human-gate` record | **compiler**: takes `&Clearance` |
| 2 Human Gate **approval** | `HumanGateApprove` | `orchestration::gates::answer` — the only writer of `ANSWERED` | calls `guard_effect` |
| 3 release certification | `ReleaseCertification` | `release::build` — the only minter of a certified release | calls `guard_effect` |
| 4 trust-policy mutation | `TrustPolicyMutation` | `srr::state::MachineState::set_root_metadata` — the only writer of `trust/root.json` and the provisioning latch | calls `guard_effect_on` |
| 5 privileged plugin acquisition | `PrivilegedPluginAcquisition` | `srr::plugins::guard_acquisition` — the only acquisition decision | calls `guard_effect` |
| 6 floor lowering | `FloorLowerOrReset` | **no primitive exists**: `Floors` exposes only `raise_*`, which ignore a lower value | asserted, not assumed |
| 7 presenting below-floor as current | — | **no primitive exists**: every reporting surface carries the marking | asserted, not assumed |

### The witness type, and where it is *not* used

`breakglass::Clearance` has private fields, one private constructor (`issue`), no `Clone`, no `Copy`, no
`Default`. No value of it can exist outside `breakglass`. `gates::build` takes a `&Clearance`, so **a new
gate-raising function inside `gates.rs` does not compile until it has asked §6** — the compiler places the
enforcement point, not a reviewer's memory.

It is deliberately **not** how `set_root_metadata`, `release::build` or `guard_acquisition` are gated. A token
handed in by a caller is a decision taken at some earlier moment; those sinks ask the question at the instant of
the effect. Where a sink has a small fixed set of in-module wrappers the type system carries the proof the last
few lines without opening a time-of-use gap; where it does not, the check is inside the sink. The trade is stated
so the next verifier can disagree with it explicitly rather than have to infer it.

### Why the *operation*-level guard was also added to `provision.rs`

`gov trust root-update` and `gov trust provision` are §6-named operations that reach no operation-level
chokepoint. `breakglass::guard(&ms, FRAMEWORK_NAME, "trust root-update")` is now the first act of `root_update`,
so the refusal happens before any signature work and reads as the operation the operator typed. The effect is
independently refused at the sink if that line is ever lost. This is redundancy on purpose, at the exact place the
finding was.

`provision` takes the same guard, but **after** its `SRR_ALREADY_PROVISIONED` check — see §7.

---

## 2. The coverage test, and what it would have caught

`tests/certification/srr.rs::section_6_effects_are_enforced_inside_their_sinks`, in two halves.

### A — the mechanism, read off the candidate's own source

| # | asserts | fails when |
|---|---|---|
| A1 | `SECTION_6_SINKS` covers every `REFUSED_ACTIVITIES` entry, once | a §6 bullet loses its sink |
| A2 | each named sink's own body contains the enforcement call for its own effect | the check is moved out of the effect |
| A3 | `gates::build` still takes `&Clearance`; `create` and `create_system` still acquire one | the compile-time guarantee is relaxed to a convention |
| A4 | `Clearance` has no public field, one private constructor, no derive of `Clone`/`Default`, and is constructed nowhere outside `breakglass` | the witness stops being sealed |
| A5 | `AuthenticatedRelease` still holds the private `admitted` seal; `Admitted::by_admit()` has exactly **1** call site; exactly **1** struct literal in the tree | `AR29-N1` regresses |
| A6 | **no second implementation of a §6 primitive**: `new_record("human-gate"` appears in exactly one file; `root_metadata_path()` in exactly two (one writer, one reader); `Floors` has exactly three mutators and all are monotonic raises | someone adds a *new way* to perform a forbidden effect |

A6 is the assertion that matters for the class. A new *caller* is already safe, because the sink enforces. A new
*primitive* is the way the property could be lost again, and A6 fails on it.

### B — reachability, measured on a machine in genuine owner-authorised break-glass

Every probe drives the real `gov` binary after a real signed break-glass entry through `admit`.

| probe | §6 | measured |
|---|---|---|
| B1 | bullet 4 | `gov trust root-update` with a successor signed by **both** quorums → `SRR_BELOW_FLOOR_REFUSED`; anchor version unchanged; `root` metadata high-water unchanged |
| B2 | bullet 4 | `gov trust provision` → `SRR_ALREADY_PROVISIONED` (the accurate diagnosis, see §7) |
| B2b | bullet 4 | `MachineState::set_root_metadata` — **the sink** — → `SRR_BELOW_FLOOR_REFUSED`, class `trust_policy_mutation`, bullet 4 |
| B3 | bullet 2 | `gov gate create` → refused, class `human_gate_create` |
| B4 | bullet 2 | structural: the enforcement point now sits in the span `AR29-B2` measured as empty |
| B5 | bullet 2 | `gov kernel override` **on a genuinely tampered kernel** → refused. This is the caller AR-0029 disclosed it could not drive end to end |
| B6 | bullet 3 | `gov release build --certification CERTIFIED` → refused, and nothing is written |
| B7 | §5/§7/§10 | `kernel reinstall` still restores, offline, and clears the marking |
| B8 | — | once out of break-glass, `trust root-update` and `gate create` both work again |

`an_allow_listed_operation_cannot_create_a_human_gate_below_floor` carries `AR29-B2`'s second limb end to end: a
machine installed on 4.1.1, in genuine break-glass, running `gov update --apply` toward an uncertified 4.1.5 →
`SRR_BELOW_FLOOR_REFUSED` with `operation = "gate create (update --apply)"`; **no gate record written**, the lock
still at 4.1.1; the refusal names `kernel reinstall` / `update --rollback`; and that route then clears the
marking. Above floor the ordinary `HUMAN_GATE_REQUIRED` flow resumes.

**Would it have caught candidate 2?** B1 and B2b are `AR29-B1` verbatim, B3/B4/B5 are `AR29-B2`, and A2/A3 fail
outright on candidate 2's source. AR-0027's `d3` could not, because it swept operation *labels* through the guard;
these drive *operations* and inspect *effects*.

---

## 3. `AR29-C1` — two readers of one record, made one

`read_marking` is now the **only** reader of `degraded/<product>.json`. `Degraded::load` resolves through it, so
an unreadable record is `Some(Degraded { … })` rather than `None`, and every consumer —
`is_degraded`, `gov trust status`, `gov trust break-glass`, `gov recover`, `try_exit` — agrees with the guard.

The half that was actually broken was the **exit**: `try_exit` now receives a `Degraded` for an unreadable record
and rewrites it on a satisfied `OWNER-DECISION-0006` §7 exit, so restoring an authenticated release at or above
both floors clears the marking and governed operation resumes. Verified across all seven of AR-0029's corruption
shapes (`an_unreadable_marking_is_read_the_same_way_by_every_consumer_and_still_exits`).

**The exit policy is untouched.** `exit_satisfied` and `EXIT_POLICY = "b_stricter_both_floors"` are unchanged and
remain the single owner-decided exit-floor comparison; the same test re-asserts that a release below the stricter
floor, and an unauthenticated release at it, both still fail to clear. `SRR2-R1-C1` was not widened.

AR-0029's `ho_c_deadlock::c3` and `::c4` flip from failing to passing.

---

## 4. `AR29-N1` — sealed, not restated

`AuthenticatedRelease` now holds a private, zero-sized `admitted: sealed::Admitted`. `Admitted`'s only constructor
is `pub(super) fn by_admit()`, called from exactly one place: the tail of `admit_inner`. A struct literal from any
other module, or any other crate, **does not compile**.

"Constructible only by `admit`" is now the type property the architecture has been claiming. The five-admit /
five-`install_kernel` census still runs and now checks something narrower: that the seal has one call site.

**This has a cost and it is not hidden.** AR-0029's `ho_f_preservation` binary no longer compiles, because its
`f4` *is* the struct literal the seal forbids:

```
error: cannot construct `AuthenticatedRelease` with struct literal syntax due to private fields
```

That error is the finding closing. But `ho_f` also carried six preservation checks unrelated to `f4`, and losing
them silently would be the kind of quiet evidence loss this phase exists to prevent. They are reproduced in the
product's own suite as `the_no_bypass_and_no_signing_preservation_census_still_holds` — f1 (no permissive
verifier in scope, no bare `.verify(`), f2 (no signing capability, `SRR-R0-L4` vacuous), f3 (5 `admit` / 5
`install_kernel`, no path-taking variant), f5 (D-0007 reads none of the SRR verdicts and vice versa), f7 (floors
monotonic, and an unauthenticated observation raises nothing). f6 (Contract v3 digest) was already covered by
`the_capability_contract_source_chain_is_hash_bound_and_fails_closed`.

Only `AuthenticatedRelease` is sealed. `Staged`, `MachineState` and `Floors` keep public fields: they carry no
"constructible only by" claim, and sealing `Floors` would additionally break `ho_a` and `ho_c`, which construct it
legitimately. No claim anywhere in the repaired source says otherwise.

---

## 5. `AR29-N3`, `N4`, `N5`

* **`N3` — one spelling of the marking path.** `state::degraded_path_at(root, product)` is now the single path
  builder; `MachineState::degraded_path` delegates to it and `guard_light` uses it instead of its own weaker
  sanitiser. Byte-identical output for the current `FRAMEWORK_NAME`; the latent silent §6 bypass for any other
  product string is gone. `resolve_state_root` and `default_state_root` are **not** in the diff — `AR27-OD1` and
  `OWNER-DECISION-0007` §1 are out of scope and machine-state *root* resolution did not change.

* **`N4` — the allow-list and the behaviour now agree.** `BELOW_FLOOR_LIMITS` states, per allow-listed entry,
  where §6 still bites; `GATE_FREE_RESTORATION_ROUTES` names the ways out. Both are surfaced in every refusal's
  `details` and in the durable break-glass entry record, so the operator reads the limit at the moment it bites.
  The refusal for `update --apply` is taken at the same enforcement point the gate sink uses, before any protected
  write. `PERMITTED_OPERATIONS`' doc states it: an entry permits the operation, it does not suspend §6 inside it.
  The tuple shape of `PERMITTED_OPERATIONS` and `REFUSAL_CLASSES` is unchanged.

* **`N5` — the phantoms are gone from the live table and made verifiable.** `REFUSAL_CLASSES` now holds only
  labels this product actually passes to an enforcement point. The ten names that no operation carries moved to
  `RESERVED_REFUSAL_CLASSES`, which is explicitly a statement that the operation **does not exist** — the opposite
  of a coverage claim — and is as inert as the live table. `section_6_refusal_class_tables_are_partitioned_by_what_the_product_actually_enforces`
  derives the enforced-label set from the product's own call sites and fails if a live entry names no operation,
  or if a reserved name acquires one. That is the mechanism behind AR-0027's false negative, closed at the source.

  Both tables remain reporting-only. `refusal_class` consults live then reserved, so existing behaviour
  (`release certify` → `release_certification`) is unchanged and no pre-existing assertion had to move.

---

## 6. Regression and the two prior held-out suites

Toolchain `cargo 1.98.1 (797e8a9bc 2026-08-05)`. Every run stripped of the nine refused-authority variables plus
`GOV_MACHINE_STATE_DIR`.

| Suite | Baseline at `f5717a9` | After | File |
|---|---|---|---|
| `cargo test --lib` | 31 passed, 0 failed | **36 passed, 0 failed** | `evidence/REGRESSION-LIB.txt` |
| `cargo test --test certification` | 65 passed, 0 failed | **70 passed, 0 failed** | `evidence/REGRESSION-CERTIFICATION.txt` |
| `cargo clippy --all-targets` | clean | clean (0 warnings, 0 errors) | — |

All 31 pre-existing lib tests and all 65 pre-existing certification tests still pass. **No pre-existing test was
edited and no assertion was weakened**: `git diff --numstat` on `tests/certification/srr.rs` is **866 insertions,
0 deletions**. The deltas are 5 new lib tests (all in `srr::breakglass`) and 5 new certification tests.

### AR-0027's held-out suite (`evidence/AR-0027-HELD-OUT-RERUN.txt`)

| File | AR-0027 on candidate 1 | repair 1 | **repair 2** |
|---|---|---|---|
| `heldout_srr` | 12 / 0 | 12 / 0 | **12 / 0** |
| `heldout_srr2` | 8 / 0 | 6 / 2 | **6 / 2** |
| `heldout_srr3` | 5 / 0 | 4 / 1 | **4 / 1** |
| `heldout_srr4` | 4 / 0 | 4 / 0 | **4 / 0** |
| total | 29 / 0 | 26 / 3 | **26 passed / 3 failed** |

Identical to repair 1, as expected: `b1`, `b2` (`AR27-N1`) and `d3` (`AR27-B1`) are the three `OBSERVED:`
weakness assertions closing. `d3`'s census is unchanged — 32 refused, 3 permitted — so repair 1's `AR27-B1`
closure is intact.

### AR-0029's held-out suite (`evidence/AR-0029-HELD-OUT-RERUN.txt`)

| File | AR-0029 on candidate 2 | **repair 2** |
|---|---|---|
| `ho_a_allowlist` | 6 / 0 | **6 / 0** |
| `ho_b_coverage` | 4 / 2 | **4 / 2** |
| `ho_c_deadlock` | 3 / 2 | **5 / 0** |
| `ho_d_expiry` | 5 / 0 | **5 / 0** |
| `ho_e_rootexpiry` | 6 / 0 | **6 / 0** |
| `ho_f_preservation` | 7 / 0 | **does not compile** (see §4) |
| total | 31 / 4 | **26 passed / 2 failed of 28 compiled; 7 not run** |

**All four `OBSERVED:` failures flipped to passing**, which is the repair:

| test | finding | now |
|---|---|---|
| `ho_b_coverage::b1` | `AR29-B1` | `gov trust root-update` returns `Err("SRR_BELOW_FLOOR_REFUSED")`; anchor 1 → 1; no keys revoked |
| `ho_b_coverage::b2` | `AR29-B1` | anchor version 1, `root` metadata high-water 0 — nothing moved |
| `ho_c_deadlock::c3` | `AR29-C1` | the §7 exit condition clears an unreadable marking |
| `ho_c_deadlock::c4` | `AR29-C1` | the machine no longer reports the opposite of what it enforces |

**Two tests flipped from passing to failing, and both are structural census tripwires doing their job.** Neither
pins a behaviour; each asserts the *absence* of a guard, with a message asking for the census to be re-derived:

| test | assertion | message |
|---|---|---|
| `ho_b_coverage::b3` | `!root_update.contains("breakglass::guard")` | `root_update unexpectedly guards; re-derive this census` |
| `ho_b_coverage::b6` | the span between the allow-list entry and `gates::create_system` contains no guard | `a guard now sits between the allow-list entry and the gate creation` |

Both statements are now true, which is the point of the repair. `b3`'s printed census ("`provision::root_update`
UNGUARDED", "`create_system` UNGUARDED", "`release::build` UNGUARDED") is stale and should be re-derived by the
next verifier.

`ho_b_coverage::b4` and `b5` pass, so §5 inspection, diagnosis, repair, backup/export and restoration all remain
reachable below floor, `break-glass` still reports `network_required = false`, and provisioning still cannot
re-anchor a provisioned machine.

---

## 7. One deliberate behaviour decision, stated rather than buried

`provision::provision` takes its §6 guard **after** the `SRR_ALREADY_PROVISIONED` check, not before.

Placing it first was tried and changed `ho_b_coverage::b4` from `SRR_ALREADY_PROVISIONED` to
`SRR_BELOW_FLOOR_REFUSED`. That is a behaviour AR-0029 verified as *satisfied*, and on inspection the earlier
order is also the worse message: a machine cannot carry the marking without already holding a trust anchor (the
marking is written by `enter`, which needs the root's `recovery` role), so on every marked machine that door is
already shut, and telling the operator "below floor" implies the command would work once they leave break-glass —
which is false. The order was reverted; `b4` passes; the §6 guard is kept for the case that is not reachable
today, and the effect is refused at the sink regardless (measured as B2b).

---

## 8. Preservation obligations — re-verified after the repair

| Obligation | Check | Result |
|---|---|---|
| Compiler-enforced no-bypass | `install_kernel` takes `&AuthenticatedRelease`, now **sealed** with a private field | strengthened; one `by_admit` site, one literal |
| Allow-list shape, `permitted_activity`, `REFUSAL_POLICY` | `ho_a` 6/6: 63 near misses / 0 permitted, exactly four permitted, `REFUSAL_CLASSES` inert | unchanged |
| Expiry canonical-form gate, `ROOT_EXPIRY_PROFILE` | `ho_d` 5/5, `ho_e` 6/6 | unchanged |
| `crypto::verify` strict-only | `heldout_srr::a10` passes; new census asserts no `Verifier` import and no bare `.verify(` | unchanged |
| Exactly five `admit` / five `install_kernel` sites | new certification census | **5 / 5** |
| Floors at all six ingresses, advancing last | `verifier.rs` ingress set and `staging.rs` untouched | unchanged |
| Transaction abort not a bypass | `update.rs` rollback path untouched | unchanged |
| D-0007 separate, establishes **intact** only | new census asserts both directions | preserved |
| `SRR-R0-L4` vacuous | new census: no `SigningKey`/`Signer`/`PRIVATE KEY` outside the secret *detector* | preserved |
| `gov` verifies, never signs | `crypto.rs` not in the diff | preserved |
| Contract v3 canonical import byte-identical | `4c2df291…` == repository-root source | identical |
| `SRR2-R1-C1` untouched | `EXIT_POLICY = "b_stricter_both_floors"`, `exit_satisfied` unchanged, still the single exit-floor comparison | unchanged, not widened |
| `SRR-R0-L7` | no offline first install added; `ho_b::b5` asserts `network_required = false` | unchanged |
| All twelve frozen R1 items | no frozen-boundary content touched | unchanged |

## 9. Out of scope — not touched

* **`AR27-OD1` / machine-state path resolution**: `resolve_state_root` and `default_state_root` are **not in the
  diff**. `degraded_path_at` resolves a path *within* an already-resolved root and produces byte-identical output.
* **`SRR2-R1-C1`**: `exit_satisfied` and `EXIT_POLICY` unchanged, still the single exit-floor comparison. `AR29-C1`
  was closed at the *readability* of the marking, not at the exit policy.
* R2-lifecycle `AR29-N2`, `AR27-N3`, `N5`, `N6`, `N7`: recorded, carried, untouched.
* `SRR-R0-L7`: no first-install ceremony added.
* No RoT-1 Revision 8, no CP-1 resumption, no D-0008/ARCH-0002 activation. No owner record, frozen boundary,
  `release/verification/**`, `release/root-of-trust/*-review*/**` or `release/releases/**` content was modified.
  Neither held-out suite was edited; both were copied byte-identically and re-run.

## 10. Nothing stubbed. What I could not prove.

Nothing in this repair is stubbed, mocked or partially implemented. No `NEW_OWNER_DECISION_REQUIRED` item arose:
`AR29-B1` and `AR29-B2` implement a policy the owner already decided in `OWNER-DECISION-0006` §6.

Stated plainly, because surfacing a suspicion beats a clean-looking report:

1. **`guard_effect` fails open when `resolve_state_root()` errors**, exactly as `guard_light` has since repair 1.
   That is the "this machine has no protected state at all" case, and changing it would mean changing
   machine-state root resolution, which `OWNER-DECISION-0007` §1 puts out of scope. It is inherited, not
   introduced, and it is the one place a §6 check can be skipped without a code change.
2. **§6 bullet 7** ("treating the below-floor release as current or fully trusted") has no sink because it has no
   primitive — every reporting surface I inspected carries the marking. I verified `gov trust status`,
   `gov trust break-glass` and `gov recover`, and `AR29-C1` closed the case where they disagreed with the guard.
   I did **not** audit every other JSON surface (`gov status`, `gov doctor`, telemetry) for a field that could be
   read as "current and fully trusted" without the marking beside it. I believe bullet 7 holds; I did not prove it
   exhaustively.
3. **§6 bullet 5's sink is the acquisition *decision*, not a byte-installing primitive.**
   `plugins::guard_acquisition` has one caller today (`capabilities::governance::register`); `tools::install`
   reaches the same effect through the operation-level guard only. If a future path installs a privileged
   capability without consulting `guard_acquisition`, the effect-level point would be missed. The coverage test
   pins the sink but does not prove `guard_acquisition` is unavoidable the way `set_root_metadata` and
   `gates::build` are.
4. **`Clearance` is a witness, not a capability with a lifetime.** Where it is passed (`gates::build`) the gap
   between acquisition and use is a few lines within one function. It is not a defence against a long-lived token,
   and nothing in the product holds one.
