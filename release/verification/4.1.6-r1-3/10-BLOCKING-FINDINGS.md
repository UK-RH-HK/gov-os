# AR-0031 — blocking findings on `srr1-r1-candidate-3`

Two. Verdict `BLOCKING_FINDINGS_PRESENT`. `GATE-R1-CANDIDATE-ACCEPT` is not satisfied.

Neither is `REQUIRES_R0_OR_OWNER_ADJUDICATION`. Neither triggers `R0_OWNER_READJUDICATION_REQUIRED`.

---

## `AR31-B1` — §6 bullet 7 is enforced nowhere, and the census entry that excuses it is false

| Field | Value |
|---|---|
| Severity | **HIGH** |
| Normative source | `OWNER-DECISION-0006` §6 bullet 7 (`90340772…`): while marked `DEGRADED — RECOVERY ONLY`, the product MUST NOT treat "the below-floor release as current or fully trusted" |
| Provenance class | falsifies a claim the candidate makes about itself (`breakglass::SECTION_6_SINKS`) **and** falsifies the normative MUST NOT directly |
| Lifecycle / gate | **R1** — `GATE-R1-CANDIDATE-ACCEPT` |
| Classification | **Residual** of `AR29-B1`/`AR29-B2` |
| Evidence | `hx_a::a8`; re-derived by hand from `runtime/src/doctor.rs`, `runtime/src/update.rs`, `runtime/src/context/mod.rs`, `cli/src/main.rs` |

### The claim under test

`breakglass::SECTION_6_SINKS` entry seven reads, verbatim:

```
("present_below_floor_release_as_current", "no primitive: every reporting surface carries the marking")
```

and the module header explains: "Bullets 6 and 7 have no sink because they have no primitive … every surface that
reports the installed release carries the marking alongside it." The repair states it verified `gov trust status`,
`gov trust break-glass` and `gov recover`, and that it did **not** exhaustively audit `gov status`, `gov doctor` or
telemetry.

### What I found

**First: nothing is ever refused under bullet 7.** `Effect::PresentBelowFloorReleaseAsCurrent` has **no call site
anywhere in the product** outside `breakglass.rs` itself, where it appears only in the enum declaration, in
`Effect::activity()`, and in two of the module's own unit tests. The bullet is declared, named and reportable, and
is enforced at no point. The whole of bullet 7 therefore rests on the prose assertion above.

**Second: the assertion is false.** The three surfaces the repair checked do carry the marking. The ones it did not
audit do not:

| surface | file | marking? | what it emits on a marked machine |
|---|---|---|---|
| `gov doctor` | `runtime/src/doctor.rs` | **no** — the file contains **zero** occurrences of `breakglass`, `is_degraded`, `Degraded` or `below_floor` (`grep -c` = 0) | a `verdict` beside `framework_version`. A function holding no reference to the marking cannot emit it. Aggravating: `doctor`'s own verdict vocabulary already contains the string `DEGRADED` meaning "medium/low check failures", so the one word an operator scans for is taken by an unrelated meaning |
| `gov update --check` | `runtime/src/update.rs`, `fn check` | **no** | `{"current": <below-floor version>, "up_to_date": …, "recommendation": "nothing to do"}`. This is §6 bullet 7 in the decision's own words: the below-floor release, labelled `current`, with the operator told there is nothing to do — when in fact restoring an authenticated at-floor release is the only way out of break-glass. It is read-only, so it never reaches `control::guard_write` and nothing refuses it |
| `gov version` | `cli/src/main.rs` | **no** | `{"framework": …, "version": …}`. Opens no project and consults nothing |
| agent context packet | `runtime/src/context/mod.rs` | **no** | `"project_state": {"framework_version": …}` inside the deterministic-hashed packet every kernel role reads |

### Consequence

On a machine in genuine owner-authorised break-glass, the two surfaces an operator reaches for first — "is this
machine healthy?" and "am I up to date?" — both answer as though the machine were not in break-glass, and the
machine-readable packet every agent consumes says the same. The marking exists to stop exactly this. This is not a
privilege escalation; it is the defeat of the operator-facing control the marking *is*.

### Bounded counterexample

`gov doctor` on a marked machine: `doctor::run` computes 29 checks and a verdict without reading any break-glass
state, because no such read exists in the file. There is no input that makes it mention the marking.

### Residual, and why — not a materially new class

`AR29-B1`/`AR29-B2` were named as one class: **an effect that reaches no enforcement point**. Repair 2's answer to
that class was the sink census. For bullets 2–5 the repair found the primitive and put the check inside it. For
bullet 7 it asserted that no primitive existed and therefore no check was needed — and the assertion is wrong, so
the reporting surfaces that realise the bullet-7 effect reach no enforcement point. That is the same class, closed
incompletely, not a new mechanism. I considered and rejected calling it new: nothing here is a novel failure mode,
only the same coverage gap surviving in the two bullets the census excused instead of instrumented.

### What would close it

Not my call to design, but the shape is constrained by the census's own logic: either a primitive is identified for
bullet 7 and the check moves inside it, or the "no primitive" claim is made true by giving every surface that
reports the installed release or a trust verdict the marking beside it — and, so the claim stops being
unfalsifiable, a test that drives those surfaces on a marked machine and asserts the marking is present. The
existing census test cannot fail on this: its A2 loop iterates only the five sinks that name a function and
silently skips the two whose sink string begins `"no primitive:"`.

---

## `AR31-B2` — both §6 enforcement points fail open on the one input the product classifies as hostile

| Field | Value |
|---|---|
| Severity | **MEDIUM** |
| Normative source | frozen R1 boundary item 9 (`70977d11…`): "project, CLI, environment, model and plugin inputs cannot create trust or approval"; `OWNER-DECISION-0007` §1, which states `GOV_MACHINE_STATE_DIR` "remains refused on a provisioned machine"; and the candidate's own §6 claim in `breakglass.rs` |
| Provenance class | **falsifies a claim**, twice: the repair's claim that a path reaching the effect "cannot miss" the enforcement point, and the repair's stated reason for leaving it open |
| Lifecycle / gate | **R1** — `GATE-R1-CANDIDATE-ACCEPT` |
| Classification | **Materially new class** — with the qualification in the note below, which matters for the convergence decision |
| Evidence | `hx_b::b1`–`b6` |

### The defect

`guard_effect` and `guard_light` each contain:

```rust
let Ok(root) = crate::srr::state::resolve_state_root() else {
    // No protected machine state resolves here, so there is no marking on this machine to enforce: the
    // ungoverned/unprovisioned case, not a degraded one. ...
    return Ok(...);
};
```

Both limbs of that comment are wrong.

**Limb one is factually wrong about when the branch is taken.** I enumerated every input to `resolve_state_root()`
(`hx_b::b1`):

| input | result |
|---|---|
| unprovisioned, no override | `Ok(default)` |
| unprovisioned, `GOV_MACHINE_STATE_DIR` set | `Ok(override)` — the documented ARCH-0003 §8 CI-runner path |
| provisioned, no override | `Ok(default)` |
| **provisioned, `GOV_MACHINE_STATE_DIR` set to a different path** | **`Err(SRR_PROTECTED_STATE_OVERRIDE_REFUSED)`** |

The ungoverned/unprovisioned case returns `Ok` and never reaches the fail-open. The **only** input that reaches it
is an environment variable attempting to relocate a provisioned machine's protected floors — which is the case the
product detects and names as a refusal. The guards fail open on precisely the input the product refuses.

**Limb two is wrong about the fix.** `OWNER-DECISION-0007` §1 closes `AR27-OD1` and binds that "no repair role may
change machine-state path resolution on its account". The fail-open is not in path resolution. It is two
`let … else { return Ok(…) }` blocks in `breakglass.rs` and nowhere else in the tree (`hx_b::b6` measures this).
`resolve_state_root` and `default_state_root` are byte-identical across the repair and would remain byte-identical
under a fix that returns the error instead of a clearance. No legitimate input reaches the branch, so failing
closed costs nothing. **This is therefore repairable within R1 and is not `REQUIRES_R0_OR_OWNER_ADJUDICATION`** —
the one point where I disagree with the repair's own routing.

### Bounded counterexample

On a provisioned machine genuinely marked `DEGRADED — RECOVERY ONLY`, with the marking record present and
`is_degraded` returning `true` throughout:

```
export GOV_MACHINE_STATE_DIR=/any/other/path
```

* `guard_effect` returns `Ok(Clearance)` for **all eight** §6 effects — `normal_privileged_operation`,
  `human_gate_create`, `human_gate_approve`, `release_certification`, `trust_policy_mutation`,
  `privileged_plugin_acquisition`, `floor_lower_or_reset`, `present_below_floor_release_as_current` (`hx_b::b2`).
* `guard_light` returns `Ok` for every label tried — `gate create`, `gate answer`, `plugins register`,
  `tools install`, `cit execute`, `task create`, `trust provision` (`hx_b::b3`).

Both enforcement points fail open **together**, so an operation carrying a bullet 2–7 effect loses both checks at
once. The sharpest case (`hx_b::b4`): `gates::create_system` was deliberately left with no operation-level guard
because the sink was supposed to suffice. Under the override its only §6 control issues a `Clearance`;
`gates::build` takes that `&Clearance` as proof the question was asked and performs no further check; a Human Gate
is created below floor. `gates::answer` loses its check on the same input, so the gate is then approvable. An
environment variable has produced a Human Gate approval on a below-floor machine.

`set_root_metadata` is the exception and the proof of the diagnosis: it uses `guard_effect_on`, which takes the
`MachineState` and resolves nothing, so bullet 4 holds under the identical input (`hx_b::b5`).

### Why MEDIUM rather than HIGH

`OWNER-DECISION-0007` §1 accepts as in-boundary that an owner-privileged process can relocate machine state via
`HOME`/`XDG_STATE_HOME`, citing ARCH-0003 §1's disclaimer of protection from a hostile local admin. An attacker who
can set `GOV_MACHINE_STATE_DIR` can set `XDG_STATE_HOME`, which points the product at an empty, unmarked state root
and bypasses §6 by that owner-accepted route. So this finding grants no capability that is not already
in-boundary, and I do not claim a novel privilege escalation.

It blocks on the other limb of the handoff's rule — **it falsifies an R1 claim**. Three specific claims:

1. `breakglass.rs`'s central assertion that "a caller that has not been written yet still reaches the effect only
   through its sink, and the sink refuses". Here the sink is reached and issues a clearance.
2. `OWNER-DECISION-0007` §1's statement that `GOV_MACHINE_STATE_DIR` "remains refused on a provisioned machine" —
   true of `resolve_state_root`, false of the two §6 guards that consume it.
3. The repair's own out-of-scope routing, which would have left this to the owner when it is a two-line local fix.

The distinction that matters operationally: via `XDG_STATE_HOME` the product is *coherent* — it believes it is a
different, unprovisioned machine and behaves that way throughout. Via `GOV_MACHINE_STATE_DIR` it is *incoherent* —
it simultaneously refuses to resolve its protected state (so `MachineState::open()` errors and `gov trust status`
fails) and permits §6-forbidden effects against the machine it is still marked on.

### Classification note — materially new, and what that does and does not mean here

**It is a materially new class.** It is not `AR27-B1`: the decision procedure is a correct allow-list class
control and I could not break it (`hx_d::d5`, twelve near-miss forms per allow-list entry). It is not `AR29-B1`/`B2`: the guard **is** on
the path and **is** called. It is a third mechanism — *the enforcement point resolves its own subject, and treats
"cannot determine" as "permit"*. I will not shade this into a residual to keep the phase alive; none of the two
prior findings names it.

**But it differs from the prior two in provenance, and the orchestrator should weigh that.** Iterations 1 and 2
each closed their findings and then a new class surfaced *one level deeper, undisclosed*. This one was **inherited
from repair 1** (`guard_light` has carried it since then), was **present and visible in candidate 2**, was not
raised by AR-0029, and was **explicitly disclosed by repair 2 and routed to me for adjudication**. It is not a new
depth that this repair's work uncovered; it is a known defect reaching its first adjudication. The genuinely
new-to-this-iteration, undisclosed blocking finding is `AR31-B1`, and that one is a **residual**.

---

## Convergence statement

For the orchestrator's stated rule, accurately:

* **Blocking findings: 2.** One residual (`AR31-B1`, HIGH), one materially new class (`AR31-B2`, MEDIUM).
* **Undisclosed blocking findings new to this iteration: 1** — `AR31-B1`, a **residual**.
* **The materially new class (`AR31-B2`) was disclosed by the repair itself** and is inherited from repair 1.

Whether that constitutes "a third materially new class" for the purposes of
`PHASE_CONVERGENCE_ESCALATION_REQUIRED` is the orchestrator's call, not mine, and I have deliberately not shaded
the label either way to influence it. My own reading, offered without prejudice to that decision: both findings are
bounded, locally repairable, and neither requires an owner decision or a boundary change — which is a materially
different situation from the two prior iterations, where each new class required rethinking the control's shape.
