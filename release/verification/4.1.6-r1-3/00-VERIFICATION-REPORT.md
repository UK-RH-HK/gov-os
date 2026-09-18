# AR-0031 — fresh independent R1 candidate verification, iteration 3

| Field | Value |
|---|---|
| Run | AR-0031, `role: verifier-c` |
| Handoff | `HO-0031-r1-reverification-2.md` |
| Candidate | `srr1-r1-candidate-3` (repair work commit `748c5d3`, AR-0030) |
| Worktree HEAD verified | `26bfe9bbf9141a4d27126da0d09bbeceb4a395d7`, branch `phase1/srr1-r1-verify-3` |
| Active gate | `GATE-R1-CANDIDATE-ACCEPT` |
| Toolchain | `cargo 1.98.1 (797e8a9bc 2026-08-05)` |
| **Verdict** | **`BLOCKING_FINDINGS_PRESENT`** |

## Independence

I authored none of this candidate: not the implementation (AR-0026), not repair 1 (AR-0028), not repair 2
(AR-0030), not AR-0027's or AR-0029's verifications, and not the architecture. I authored my own held-out suite
(`evidence/heldout-tests/`, crate `srr-heldout-ar0031`), which shares no source line with either prior harness. I
modified no product source, no frozen boundary document, no owner record, and neither prior verification's
evidence; this directory is my only addition.

**Delegation disclosed.** I used one read-only sub-agent for a single breadth sweep: enumerating the product's
release/trust *reporting* surfaces for the §6 bullet 7 question. It made no judgement that I relied on. Every
claim it returned that appears in this report I re-derived myself directly from the source
(`Effect::PresentBelowFloorReleaseAsCurrent` call-site census, `doctor.rs` marking-reference count,
`update::check`'s emitted object) and then pinned in a held-out test. All classification, severity and verdict
work is mine.

## Summary

The candidate's §6 effect-level enforcement is a real and substantial improvement, and it closes AR-0029's two
assigned findings completely. Four of the six census bullets that name a sink are sound, and I could not break
them. Two blocking findings remain.

| ID | Severity | What | Residual or materially new |
|---|---|---|---|
| `AR31-B1` | HIGH | §6 bullet 7 is enforced nowhere and its "no primitive exists" census entry is false: `gov doctor`, `gov update --check`, `gov version` and the agent context packet all report the below-floor release as current/healthy with no marking | **Residual** of `AR29-B1`/`B2` |
| `AR31-B2` | MEDIUM | `guard_effect` and `guard_light` convert `resolve_state_root()`'s refusal into a clearance, so both §6 enforcement points fail open together on an input the product itself classifies as hostile | **Materially new class** (disclosed by the repair; inherited from repair 1, not introduced by repair 2) |

Non-blocking conditions are in `20-LATER-LIFECYCLE-CONDITIONS.md`. No item requires
`R0_OWNER_READJUDICATION_REQUIRED`, and no item is marked `REQUIRES_R0_OR_OWNER_ADJUDICATION` — see
`AR31-B2`'s adjudication note, which is the one place the repair predicted otherwise and where I disagree with
reasons.

## 1. Pinned inputs and STOP conditions

All six pinned digests verified at this commit and match both AR-0029's and AR-0030's pinned values. No mismatch;
no STOP condition. Values in `REVIEWED-CONTENT-DIGESTS.txt`.

Both prior held-out suites are byte-identical at this commit: `git log 26bfe9b -- release/verification/4.1.6-r1/evidence
release/verification/4.1.6-r1-2/evidence` returns only the two original verification commits (`26c2dc5`, `d3f52c6`),
so neither has been touched since it was written. I edited neither.

## 2. Regression, reproduced independently

```
cargo test --lib                 36 passed; 0 failed; 0 ignored     (exit 0)
cargo test --test certification  70 passed; 0 failed; 0 ignored     (exit 0)
```

Exactly the figures the repair and the orchestrator report. `git diff --numstat 748c5d3~1 748c5d3` confirms
`tests/certification/srr.rs` at **+866 / −0**, purely additive; no existing test was edited or deleted.

## 3. Item-by-item disposition of the frozen R1 section

Source: `release/root-of-trust/signed-release-root-v1/01-FROZEN-R0-R1-R2-R3-ACCEPTANCE-BOUNDARY.md`
(`70977d11…`), twelve bullets.

| # | R1 item | Disposition | Basis |
|---|---|---|---|
| 1 | a mature reviewed TUF/cryptographic implementation is used correctly | **HOLDS** | `ed25519-dalek` used through `crypto::verify`/`verify_strict` only; the permissive `Verifier` trait is out of scope crate-wide; a malleated S+L signature is refused identically by both entry points (`hx_c::c2b`, which reproduces a check that the migration dropped — see §6) |
| 2 | candidate/source files cannot create their own trusted identity | **HOLDS** | `AuthenticatedRelease` now carries a private `sealed::Admitted` seal with exactly one construction site; no struct literal compiles outside `srr::verifier` (this is why AR-0029's `ho_f` no longer compiles). `Clearance` likewise sealed (`hx_d::d4`) |
| 3 | wrong keys, modified metadata/payload/migration, replay, downgrade and expiry fail closed | **HOLDS** | AR-0027's `heldout_srr`/`srr4` (16/16) and AR-0029's `ho_d`/`ho_e` (11/11) all pass unmodified on this candidate |
| 4 | all privileged ingress paths call the common verifier | **HOLDS** | five `srr::admit(` sites paired with five `install_kernel` sites; `install_kernel` takes a typed `&AuthenticatedRelease` and there is no path-taking variant (`hx_d::d6`) |
| 5 | verified bytes are staged, installed and used without substitution | **HOLDS** | AR-0027's staging/substitution scenarios pass; `Staged`/`commit_tree` unchanged by the repair |
| 6 | staging/install/rollback/recovery are atomic and crash-safe | **HOLDS** | `write_durable` (tmp → fsync → rename → fsync dir) and `set_root_metadata`'s latch-after-anchor ordering unchanged; AR-0029's `ho_c` now 5/5 (its two `OBSERVED` failures flipped to passing) |
| 7 | metadata/release high-water is durable and monotonic | **HOLDS** | `Floors` exposes only `raise_metadata`/`raise_release`/`raise_minimum_secure`; an unauthenticated observation raises nothing (`hx_d::d11`, `hx_a::a7`) |
| 8 | post-install integrity remains distinct and D-0007 controls remain effective | **HOLDS** | `kernel_trust` references none of `srr::admit`, `AuthenticatedRelease`, `Authenticity`, `breakglass`, `below_floor`, `Floors`; `admit_inner` references no `kernel_trust` (`hx_d::d8`). D-0007 still establishes **intact**, never **authentic** or **admissible** |
| 9 | project, CLI, environment, model and plugin inputs cannot create trust or approval | **QUALIFIED — see `AR31-B2`** | `REFUSED_AUTHORITY_ENV` is unchanged at nine variables and each is refused. But `GOV_MACHINE_STATE_DIR`, which `OWNER-DECISION-0007` §1 states "remains refused on a provisioned machine", is not refused *by the §6 guards*: they convert its refusal into a clearance, and a Human Gate can then be created and approved below floor. Bounded by an owner-accepted equivalent (§5) |
| 10 | CI/multi-machine provisioning follows ARCH-0003 | **HOLDS** | `resolve_state_root` byte-identical across the repair; the CI-runner path (`GOV_MACHINE_STATE_DIR` on an unprovisioned machine) still resolves (`hx_b::b1` case 2) |
| 11 | the original product controls, Gate W and G0–G6 mappings remain valid | **HOLDS** | 70/70 certification, 36/36 lib, purely additive diff; no existing control edited |
| 12 | builder evidence and fresh independently authored held-out evidence pin the exact candidate | **HOLDS** | this run: 26 passed / 8 `OBSERVED:` findings across four independently authored groups, pinned to HEAD `26bfe9b` |

## 4. The census attack — is `SECTION_6_SINKS` complete?

This was the highest-value target and the repair recommended it. Result: **the census is sound for bullets 2
(create), 2 (approve), 3, 4 and 6, and false for bullets 5 and 7.**

| bullet | claimed sole sink | verdict | what I found |
|---|---|---|---|
| 2 create | `gates::build`, compiler-enforced `&Clearance` | **complete today, weaker than stated** | `new_record("human-gate"` occurs exactly once in the product, so there is no second path *today*. But the guarantee is scoped to the `gates` module: `build` is private, so the compiler binds new functions **inside** `gates.rs` and nothing outside it. `records::new_record`, `records::save_record` and `Record`'s fields are all `pub` and take no clearance. I minted a `human-gate` record three ways with no `Clearance` in existence (`hx_a::a5`): a non-literal type argument, `Record::set("type", …)`, and the public constructor. The certification test polices this clause with one grep for the source literal `new_record("human-gate"`, which none of the three spells. **Non-blocking** — no such path exists today — but the clause is a source-literal property, not the effect property it is described as |
| 2 approve | `gates::answer` | **complete** | the only function that moves a gate to `ANSWERED`; guarded at both the operation and the effect |
| 3 | `release::build` | **complete** | the only code that writes a caller-chosen certification status; `"CERTIFIED"` appears nowhere else as a written value (only as a comparison in `update.rs`); exactly one caller (`cli/src/main.rs:928`); guards at the top (`hx_a::a6`) |
| 4 | `MachineState::set_root_metadata` | **complete, and the strongest sink in the set** | the only writer of `trust/root.json`; the anchor path is reached from exactly two files (write in `state.rs`, read in `verifier.rs`) and is composed by hand nowhere; `trust_dir()` has no other caller. It guards under **both** the framework key and the anchor's own product key, so a successor root naming a different product cannot step around the marking. It is the one sink that uses `guard_effect_on`, and therefore the one sink immune to `AR31-B2` (`hx_a::a4`, `hx_b::b5`) |
| 5 | `plugins::guard_acquisition` | **FALSE — a second primitive exists** | `tools::install` installs a capability and never reaches the sink; it is covered only by `guard_write(p, "tools install")`. Separately, the sink calls `guard_effect` only `if is_privileged(descriptor)`, and `is_privileged` reads `required_permission_classes` out of the descriptor — so whether §6 is consulted at all for this bullet is decided by self-asserted data, unlike bullets 2, 3 and 4 whose sinks ask unconditionally. **Non-blocking**: below floor `tools install` *is* refused by the operation guard, so no live bypass follows (`hx_d::d1–d3`) |
| 6 | no primitive | **TRUE** | `Floors` exposes exactly `raise_metadata`, `raise_release`, `raise_minimum_secure`, all monotonic; `Effect::FloorLowerOrReset` has no call site outside `breakglass.rs` (`hx_a::a7`) |
| 7 | no primitive: "every reporting surface carries the marking" | **FALSE — `AR31-B1`** | see §5 |

**Second paths to a named effect:** one, at bullet 5 (`tools::install`), non-blocking. Bullets 2, 3 and 4 have no
second path in the product today; bullet 2's *type-level* guarantee is narrower than claimed but is not currently
reachable around.

## 5. The four disclosed weaknesses — independent judgement

### Weakness 1 — `guard_effect` fails open when `resolve_state_root()` errors

**Judgement: the repair's characterisation is wrong on both limbs. Blocking as `AR31-B2` at MEDIUM. NOT
`REQUIRES_R0_OR_OWNER_ADJUDICATION`.**

*Limb one — "the ungoverned/unprovisioned case".* False. I enumerated every input to `resolve_state_root()`
(`hx_b::b1`): unprovisioned with no override → `Ok`; unprovisioned with an override → `Ok`; provisioned with no
override → `Ok`; **provisioned with an override to a different path → `Err(SRR_PROTECTED_STATE_OVERRIDE_REFUSED)`**.
The unprovisioned case never reaches the fail-open branch. The *only* input that reaches it is the one the product
has already classified as an attempt to relocate a provisioned machine's protected floors. The guards fail open on
precisely the input the product refuses.

*Limb two — "closing it would mean changing machine-state root resolution, which `OWNER-DECISION-0007` §1 puts out
of scope".* False. `OWNER-DECISION-0007` §1 closes `AR27-OD1` and forbids changing **machine-state path
resolution**. The fail-open is not in path resolution; it is two `let Ok(root) = … else { return Ok(…) }` blocks in
`breakglass.rs` and nowhere else in the tree (`hx_b::b6`). `resolve_state_root` and `default_state_root` are
byte-identical across the repair and would stay byte-identical under the fix. Making the guards return the error
instead of a clearance costs nothing legitimate, because no legitimate input reaches that branch.

*What it lets through (`hx_b::b2`–`b4`).* On a provisioned machine genuinely marked `DEGRADED — RECOVERY ONLY`,
setting `GOV_MACHINE_STATE_DIR` to any other path makes `guard_effect` return `Ok` for **all eight** §6 effects and
`guard_light` return `Ok` for every operation label I tried. Both enforcement points fail open together. The
sharpest case is `gates::create_system`, which the repair deliberately left with *no* operation-level guard because
the sink was supposed to suffice: under the override its only §6 control issues a `Clearance`, and `gates::build`
performs no further check, so a Human Gate is created below floor — and `gates::answer` loses its check on the same
input, so the gate can then be approved. The one sink that survives is bullet 4's, because `guard_effect_on` takes
the `MachineState` and resolves nothing (`hx_b::b5`).

*Why MEDIUM and not HIGH.* `OWNER-DECISION-0007` §1 accepts as in-boundary that an owner-privileged process can
relocate machine state via `HOME`/`XDG_STATE_HOME`, citing ARCH-0003 §1's disclaimer about a hostile local admin.
An attacker who can set `GOV_MACHINE_STATE_DIR` can set `XDG_STATE_HOME`, which points the product at an empty,
unmarked state root and bypasses §6 by an owner-accepted route. So this grants no capability that is not already
in-boundary, which bounds the security consequence. It blocks on the other limb of the handoff's rule: **it
falsifies an R1 claim.** The module header's central assertion is that "a caller that has not been written yet
still reaches the effect only through its sink, and the sink refuses"; here the sink is reached and does not
refuse. `OWNER-DECISION-0007` §1's own text states `GOV_MACHINE_STATE_DIR` "remains refused on a provisioned
machine", and in the §6 guards it is not.

### Weakness 2 — §6 bullet 7 has no sink because no primitive is claimed to exist

**Judgement: falsified. Blocking as `AR31-B1` at HIGH.** Detail in §5 of `10-BLOCKING-FINDINGS.md`. In short:
`Effect::PresentBelowFloorReleaseAsCurrent` has no call site anywhere in the product outside `breakglass.rs`
itself, so nothing is ever refused under bullet 7; and the assertion that carries the bullet — "every reporting
surface carries the marking" — is false for `gov doctor` (zero references to the marking in `doctor.rs`; emits a
`verdict` beside `framework_version`), `gov update --check` (emits `"current": <below-floor version>`,
`"up_to_date"`, `"recommendation": "nothing to do"`), `gov version`, and the agent context packet. The three
surfaces the repair says it checked do carry it; the ones it says it did not audit do not.

### Weakness 3 — bullet 5's sink is the acquisition decision, not a byte-installing primitive

**Judgement: genuinely weaker, and the census entry is false, but it does not block R1.** `tools::install` is a
second primitive for the bullet-5 effect and never reaches the named sole sink. Below floor it is nonetheless
refused, by `guard_write(p, "tools install")` → the allow-list default-refuse. So the §6 *property* holds at that
door today; what does not hold is the *class control* the repair claims for this bullet — the coverage is
operation-level, which is exactly the arrangement the repair argued was insufficient. Recorded as a non-blocking
R1 condition (`AR31-N1`) rather than a blocker, because no reachable counterexample follows. I also record that
the privileged/unprivileged split that gates the check is descriptor-supplied (`AR31-N2`).

### Weakness 4 — `Clearance` is a witness, not a lifetime-scoped capability

**Judgement: I disagree with the trade as stated, on one specific point, and agree on the rest.**

I agree that a caller-supplied token is a decision taken earlier and that asking at the instant of the effect is
the right choice for `set_root_metadata`, `release::build` and `guard_acquisition`. `hx_b::b5` is direct evidence
for the repair's position: the one sink that asks with the `MachineState` in hand is the only one that survives
`AR31-B2`. That is a point in favour of asking at the sink, not against it.

Where I disagree is the claim made *for* the witness: "the *compiler* puts the enforcement point on the path, not
a convention and not a reviewer's memory." That is true only of new functions written **inside `gates.rs`**,
because `build` is private. It is not true of the product as a whole: the durable artefact `build` produces is
reachable through `records::new_record` + `records::save_record` with no `Clearance` in existence, which I
demonstrated three ways (`hx_a::a5`). The witness is a good local control and should stay; it should not be
described as closing the class, and the certification test that polices it should test the effect rather than a
source literal. Non-blocking (`AR31-N3`).

## 6. The three prior-evidence changes

### (1) `ho_f_preservation` no longer compiles — is the migration faithful?

**The compile error is genuine closure.** `ho_f::f4` is the literal `AR29-N1` asked to be made impossible;
`AuthenticatedRelease` now holds a private `sealed::Admitted` field, so the struct literal that *is* `f4` cannot
compile. Correct, and not a regression.

**Two of the six migrated checks were weakened in the move, and one was strengthened.** I compared assertion by
assertion (`hx_c::c1`–`c3`):

| check | disposition |
|---|---|
| f1 static half (permissive `Verifier` out of scope) | **strengthened** — `ho_f` collected and *printed* the bare `.verify(` census; the migrated test asserts it empty |
| f1 behavioural half (malleated S+L refused identically by `verify` and `verify_strict`) | **DROPPED** — the product suite cannot sign, so it cannot reproduce it. `ho_f` no longer compiles, so this check now runs nowhere in the candidate's evidence. I reproduced it in `hx_c::c2b`; **the property still holds** |
| f2 signing-capability census | reproduced in full |
| f2 second half (no `skip_verify`/`allow_unsigned`/`force_unsigned` switch outside `REFUSED_AUTHORITY_ENV`) | **DROPPED** — `grep -rn` over `tests/` finds none of these strings. I reproduced it in `hx_c::c3b`; **the property still holds** |
| f3 (five admit / five install_kernel, typed installer, no path variant) | reproduced in full |
| f5 (D-0007 independence, both directions, same six tokens) | reproduced in full |
| f6 (Contract v3 byte-identical, digest pinned, fails closed) | not in the migrated census, but independently covered by a pre-existing certification test at `tests/certification/srr.rs:967`; verified myself in `hx_d::d9` |
| f7 (floors monotonic, unauthenticated observation raises nothing) | reproduced in full |

So "six checks reproduced" is **substantially but not exactly** right: two sub-checks were lost. Both underlying
properties still hold — I measured both — so this is a loss of assurance coverage, not a live defect. Recorded as
`AR31-N4`.

### (2) `ho_b::b3` and `::b6` flipped from passing to failing — both are the repair working

Confirmed, and I re-derived rather than trusted. `b3` fails at `root_update unexpectedly guards`: on candidate 2
`provision::root_update` reached no enforcement point (`AR29-B1`); it now does. `b6` fails at `a guard now sits
between the allow-list entry and the gate creation`: `update --apply` passes the §5 allow-list at bullet 1 and then
meets a §6 guard before `gates::create_system`, which is `AR29-B2` closing. Both flips are the assertions doing
their job.

**`b3`'s printed §6 census is stale and I re-derived it for candidate 3** (`hx_c::c4`, full text in the held-out
output). The re-derived census is the bullet-by-bullet table in §4 above, plus: bullet 1's chokepoint is
`control::guard_write` → `guard_light` over 28 call sites / 23 distinct labels, and it fails open per `AR31-B2`.

### (3) `ho_b::b4` — both halves verified

*Half one:* `b4` passes again. In `srr::provision::provision` the already-provisioned latch (`SRR_ALREADY_PROVISIONED`)
precedes the break-glass guard in source order, so the accurate diagnosis survives and does not become
`SRR_BELOW_FLOOR_REFUSED` — the property AR-0029 verified (`hx_c::c6`, half one asserts the ordering directly).

*Half two:* the door is genuinely closed underneath, at the sink and independently of that ordering.
`MachineState::set_root_metadata` refuses below floor with `refused_class = trust_policy_mutation` and
`section_6_bullet = 4`, and no `root.json` is written (`hx_a::a4`, `hx_c::c6`). Both halves hold.

## 7. Owner-closed items — verified, not graded

Verified byte-identical across the repair work commit `748c5d3` by extracting each function body from
`git show 748c5d3~1:<file>` and comparing to the candidate:

| item | result |
|---|---|
| `resolve_state_root` | **IDENTICAL** (844 bytes → 844 bytes) |
| `default_state_root` | **IDENTICAL** (494 bytes → 494 bytes) |
| `exit_satisfied` | **IDENTICAL** |
| `exit_condition_description` | **IDENTICAL** |
| `EXIT_POLICY` | **IDENTICAL** (`b_stricter_both_floors`) |
| `REFUSED_AUTHORITY_ENV` | **IDENTICAL** (nine variables) |

`state.rs` (+38/−3) and `breakglass.rs` (+527/−59) were both edited and neither owner-closed item moved. The exit
comparison is still a single point: `effective_floor_sequence()` appears at most four times tree-wide, in
`exit_satisfied` and its reporting (`hx_d::d10`). **I do not grade either policy.**

`SRR-R0-L7`: break-glass remains purely local — `breakglass.rs` contains no `reqwest`, `http://`, `https://`,
`TcpStream`, `ureq` or `curl`, and every check reads local files (`hx_d::d12`). Offline first install stays absent.
Recovery works with no network.

## 8. My held-out suite

Crate `srr-heldout-ar0031`, outside the product tree and outside the workspace, depending on `gov-runtime` by
path. Four groups, 34 scenarios: **26 passed, 8 `OBSERVED:` failures.** Every failure is a finding pinned as an
assertion, not a broken test; the two harness imprecisions I hit on the first pass (a grep that matched
`update.rs`'s hard-coded `UNCERTIFIED` default, and a call-site threshold counting `breakglass.rs`'s own unit
tests) were corrected and both scenarios then passed, confirming bullets 3, 4 and 6.

| group | scenarios | result |
|---|---|---|
| `hx_a_census` — the `SECTION_6_SINKS` census | 8 | 6 pass; `a5` (bullet 2 clause is a source-literal property), `a8` (bullet 7 falsified) |
| `hx_b_failopen` — the fail-open | 6 | 3 pass; `b2`, `b3`, `b4` (`AR31-B2`) |
| `hx_c_prior_evidence` — the three prior-evidence changes | 8 | 6 pass; `c2`, `c3` (two migrated checks dropped) |
| `hx_d_acquisition_and_preservation` — bullet 5, `Clearance`, preservation | 12 | 11 pass; `d3` (bullet 5 second primitive) |

## 9. Both prior suites, rerun unmodified

**AR-0027** (`heldout_srr`, `srr2`, `srr3`, `srr4`): **26 passed, 3 failed** — exactly as predicted. The three
failures are its `OBSERVED:` weakness assertions flipping: `heldout_srr2::b1`, `::b2` and `heldout_srr3::d3`.

**AR-0029** (`ho_a`–`ho_f`): **26 passed, 2 failed**, with `ho_f_preservation` not compiling
(`cannot construct AuthenticatedRelease with struct literal syntax due to private fields`). Per group: `ho_a` 6/0,
`ho_b` **4/2**, `ho_c` 5/0, `ho_d` 5/0, `ho_e` 6/0. All four of AR-0029's `OBSERVED:` failures
(`ho_b::b1`, `::b2`, `ho_c::c3`, `::c4`) have flipped to passing. The two new failures are `ho_b::b3` and `::b6`,
both the repair working (§6). This matches the handoff's stated expectation exactly.

## 10. Carried, not raised

`AR29-N2`, `AR27-N3`, `N5`, `N6`, `N7` are R2-lifecycle and are not raised here.
