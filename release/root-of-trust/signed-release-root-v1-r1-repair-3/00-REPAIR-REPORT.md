# AR-0032 — bounded R1 **structural** repair of `srr1-r1-candidate-3`

| Field | Value |
|---|---|
| Run | AR-0032, fresh isolated R1 repair role, repair cycle 3 (structural). **Not AR-0028, not AR-0030.** |
| Handoff | `release/orchestration/phase-1/HANDOFFS/HO-0032-r1-structural-repair.md` |
| Authorisation | `OWNER-DECISION-0008` (Option B), SHA-256 `aa541eab86192c3710a76cf3119efdeb7e108891c5f0e9782a88e05a20d06518` |
| Policy implemented | `OWNER-DECISION-0006` §6, SHA-256 `903407729327d67c198c9bf97885a936c5601993e16ad76137a3106c5728d1db` |
| Branch / worktree HEAD at start | `phase1/srr1-r1-repair-3` @ `30aa98a10fd7f5ed85439b0d676761080519ceed` |
| Repairs | `AR31-B1` (HIGH), `AR31-B2` (MEDIUM), `AR31-N1`, `AR31-N2`, `AR31-N3`, `AR31-N4`, `AR31-N5`, plus the root cause |
| Verdict | **`READY_FOR_INDEPENDENT_OS_VERIFICATION`** — a readiness declaration only, never an acceptance |
| Graded by | a NEW fresh independent verifier with its own held-out tests. Not by this run. |

Files changed — all of them, nothing else:

```
cli/src/main.rs                       42 +    4 -
runtime/src/cit/mod.rs                24 +    1 -
runtime/src/context/mod.rs             8 +    1 -
runtime/src/doctor.rs                 13 +    0 -
runtime/src/records.rs                17 +    0 -
runtime/src/srr/breakglass.rs        353 +   21 -
runtime/src/srr/mod.rs                 1 +    0 -
runtime/src/srr/plugins.rs            39 +    6 -
runtime/src/srr/state.rs              38 +    0 -
runtime/src/tools.rs                   9 +    0 -
runtime/src/update.rs                 14 +    4 -
tests/certification/main.rs            1 +    0 -
runtime/src/srr/present.rs           NEW
tests/certification/section6.rs      NEW
```

`tests/certification/srr.rs` is **not in the diff**. No pre-existing test was edited and no assertion weakened; the
new tests are a new module.

---

## 1. The root cause, and what was actually changed about it

`OWNER-DECISION-0006` §6 is a **universal negative** and had been implemented three times as a **positive
enumeration** — forbidden operations, then guarded call sites, then effect primitives. Each was complete when written
and silently incomplete once the product grew an unenumerated path, and at every level the test was derived from the
same enumeration as the code, so it could not see that the enumeration was short.

Two things changed:

**The coverage claim is now derived from the product.** `section_6_coverage_is_derived_from_the_product`
(`tests/certification/section6.rs`) walks **every function** in `runtime/src` and `cli/src` — 84 files, 740 functions
at this commit — and, for each §6 effect, computes the set of functions that perform a durable write and mention one of
the product's own primitives for that effect. Every one of them must carry the enforcement or a call to the sink that
does. A new primitive appears in that set without anyone remembering to add it.

**An absence claim is now refutable.** Each effect's detector is first run against a **positive control**: a synthetic,
unguarded implementation of the effect. A detector that cannot flag its own positive control fails the suite, whatever
it then finds. `AR31-N5` was that the previous census test's loop *skipped* the two bullets claiming no primitive; the
new one refuses to pass on an empty derivation and fails outright on a `"no primitive"` sink entry, telling the author
what to assert instead.

**The full mechanism, with what it can and cannot see and what would defeat it, is in
`evidence/DERIVATION.md`.** That document is the substance of mandate parts 3 and 4 and is written to be argued with.
The two things most likely to defeat it: a new primitive that spells none of the product's existing APIs, and a new
*in-process* reporting surface (bullet 7's universality is a property of the CLI boundary, not of the library).

---

## 2. `AR31-B1` — §6 bullet 7 is enforced, and the marking claim is made true

### The primitive that did not exist

`runtime/src/srr/present.rs` is new and is bullet 7's sink. `presentation(surface)` **asks**
`breakglass::guard_effect(Effect::PresentBelowFloorReleaseAsCurrent, surface)` and the answer *is* the presentation:

* cleared → `{"below_floor": false, "presented_as": "CURRENT"}` and the release may be called current;
* refused → the refusal is **not swallowed**. It becomes `{"below_floor": true, "marking": "DEGRADED — RECOVERY ONLY",
  "presented_as": "BELOW_FLOOR_RECOVERY_ONLY", "exit_condition": …, "operator_note": …}`, and `attach()` rewrites any
  affirmative currency claim the surface was about to make.

It is deliberately **infallible**. §6 §5 requires inspection and diagnosis to stay available below floor, so bullet 7
cannot be enforced by refusing to answer. It is enforced by refusing to answer *as though the machine were current*.

`Effect::PresentBelowFloorReleaseAsCurrent` had **no call site anywhere in the product** on candidate 3. It has five
now, and four of them are outside `breakglass.rs`: `cli/src/main.rs::main`, `runtime/src/context/mod.rs::compile`,
`runtime/src/doctor.rs::run`, `runtime/src/srr/present.rs::presentation`, `runtime/src/update.rs::check`.

### Why the coverage is universal instead of a longer list

"Every reporting surface carries the marking" was a list, and the list was short. A longer list would fail the same
way. `run(&cli)` is called **once** in `cli/src/main.rs`, and its value reaches stdout only through the `match result`
that wraps it in the response envelope. That envelope now calls `present::attach`, so **every command result carries
the marking — including commands that do not exist yet and commands that have never heard of break-glass.**

The certification suite measures exactly that property rather than the list: on a machine in genuine owner-authorised
break-glass it drives `gov gate list`, `gov policy overrides` and `gov claims list` — commands with no relationship to
release identity — and asserts each envelope carries `release_trust.below_floor = true`.

### The four surfaces AR-0031 named, measured

| surface | candidate 3 | now |
|---|---|---|
| `gov doctor` | zero occurrences of `breakglass`/`is_degraded`/`Degraded`/`below_floor` in `doctor.rs` | `Report` carries `release_trust`, in **both** return paths, so it is carried by the typed value `update` and the audit suite consume, not only by the envelope. The field's doc states that `verdict: DEGRADED` (medium/low check failures) and `release_trust.below_floor` are different predicates — the word an operator scans for was already taken, so this is a separate field, not a verdict value |
| `gov update --check` | `{"current": <below-floor version>, "up_to_date": true, "recommendation": "nothing to do"}` | `up_to_date` is `false`, `recommendation` names §6 bullet 7 and the exit condition, and `release_trust` is attached. Attaching the marking beside an affirmative `up_to_date` would not have been enough: the claim itself is the forbidden presentation |
| `gov version` | `{"framework": …, "version": …}`, opens no project | covered by the envelope, like everything else |
| agent context packet | `project_state.framework_version` with no marking | `project_state.release_trust` inside the deterministic authority block, because the packet is hashed and consumed as a unit by every kernel role rather than read out of an envelope |

`gov trust status`, `gov status` and `gov recover` already carried the marking and are **unchanged**; the suite
re-asserts they still do and agree with the envelope.

And the marking **lifts**: `the_marking_is_absent_from_every_surface_on_a_healthy_machine` drives an unmarked machine
and asserts `below_floor = false`, `presented_as = CURRENT`, `marking = null`. A marking that never lifts is
indistinguishable from noise.

---

## 3. `AR31-B2` — both enforcement points fail closed on an undetermined subject

`guard_light` and `guard_effect` each contained `let Ok(root) = resolve_state_root() else { return Ok(…) }`. Both
limbs of the comment justifying it were wrong, and AR-0031 proved it: the unprovisioned case returns `Ok` and never
reaches the branch, and the only input that does is `GOV_MACHINE_STATE_DIR` relocating a provisioned machine — the one
input the product already classifies as hostile.

Both now route the error to `breakglass::undetermined_subject`, a typed refusal
(`SRR_BELOW_FLOOR_SUBJECT_UNDETERMINED`, `"subject": "UNDETERMINED"`, `"fail": "closed"`) that names the operation, the
§6 class and bullet, the cause, the environment variable to unset and the exit condition.

* **The allow-list is consulted first**, in both functions, so no §5 restoration route can ever be blocked by this. A
  lib test asserts that for all four permitted operations.
* **`resolve_state_root` and `default_state_root` are byte-identical** (`evidence/PRESERVATION.txt` compares the
  extracted function bodies against the base commit). `OWNER-DECISION-0007` §1 and `AR27-OD1` are untouched.
* **`guard_effect_on` and `guard` cannot reach it** — they are handed the `MachineState` and resolve nothing, which is
  why bullet 4 held under the identical input. Re-asserted.
* **Bullet 7 fails closed the same way**: unknown is not "no", so `presented_as` is `UNDETERMINED` and `below_floor` is
  `true`. Every command's envelope says so.

Measured end to end through the real binary (so the environment is a subprocess's and cannot race another test): on a
genuinely marked, provisioned machine with `GOV_MACHINE_STATE_DIR` pointing elsewhere, `gov gate create` (the
operation-level point) and `gov release build --certification CERTIFIED` (the effect-level point, reached from a sink
that takes no `Project`) both return `SRR_BELOW_FLOOR_SUBJECT_UNDETERMINED`, and nothing is written.

---

## 4. The residuals

### `AR31-N1` — bullet 5 has two primitives, and the census said one

`tools::install` installs a capability, writes its descriptor into `governance/project/tools/` and may run its install
command, and never reached `plugins::guard_acquisition`. It now calls
`plugins::guard_acquisition_below_floor("tools install")`, a named door in the acquisition module that asks
`guard_effect(Effect::PrivilegedPluginAcquisition, …)`. `guard_acquisition` keeps its own call at the instant of the
acquisition *decision*. Two primitives, two enforcement points, one decision — every §6 question in the implementation
still ends in the single private `decide` over the single `read_marking`.

The derived census now finds **both** capability-registry writers (`tools.rs::install`,
`capabilities/governance.rs::register`) by construction, and the certification test asserts both are covered. Note the
original signature I wrote missed `tools::install` because the marker was the exact call syntax `overlay_dir().join("tools")`
and the product spells it across four lines; the marker was widened to `join("tools")`. That is the derivation working
on itself, and it is why the positive controls matter.

### `AR31-N2` — the §6 question no longer rests on self-asserted data

`guard_acquisition` asked §6 only `if is_privileged(descriptor)`, and `is_privileged` reads
`required_permission_classes` out of the descriptor. It now asks **unconditionally**. The refusal is reported as
`privileged_plugin_acquisition` even for a capability declaring itself unprivileged, because below floor the product
has no basis for believing that declaration — ARCH-0003 §9 says descriptors cannot self-authorise, and deciding
*whether to ask the question* is a form of authorising. Nothing above floor changes: an unmarked machine clears every
effect.

### `AR31-N3` — bullet 2 is now an effect property, not a source-literal property

The compile-time `&Clearance` guarantee binds new functions **inside `gates.rs`**, because `build` is private. It does
not bind the product: `records::new_record`, `records::save_record` and every `Record` field are `pub`, and AR-0031
minted a `human-gate` record three ways with no `Clearance` in existence — one of them (a non-literal type argument)
invisible to any source scan.

`records::save_record` is now the §6 record-write sink. However a `Record` was minted, it becomes durable only there,
and that function asks §6 for every type in `breakglass::GUARDED_RECORD_TYPES` (today: `human-gate` →
`Effect::HumanGateCreate`). The `&Clearance` on `gates::build` is **kept**: the two bind different things — the
clearance binds new code inside `gates.rs` at compile time, the sink binds every writer in the product at the instant
of the write.

The derivation also surfaced two CIT mutation ops that reach a governed record path **without** passing `save_record`:
`write_file` writes arbitrary bytes to an arbitrary path, and `move_file` relocates a file. Both now parse their
content and ask §6 by the record type the bytes declare. Below floor `cit execute` is refused at the operation level
anyway, so there was no live bypass — what was missing was the effect-level control, which is the one that survives a
caller reaching those ops by another route. Reported here rather than absorbed silently: **this is a residual of
`BC-R1-2` that the new derivation found, not a finding I was handed.**

Behaviour note, stated because it is a real change: `gov gate present` calls `authority::require` and `save_record` and
**not** `control::guard_write`, so on candidate 3 it mutated a governed Human Gate record below floor. It is now
refused at the record-write sink. The certification suite drives it.

### `AR31-N4` — the two dropped sub-checks run again

`tests/certification/section6.rs::the_dropped_held_out_sub_checks_run_here` restores both:

* **`ho_f::f1`'s behavioural half** — a malleated S+L signature must be refused by both `crypto::verify` and
  `crypto::verify_strict` with the same error code. It could not move into the product's own census because that census
  reads product source and `gov` cannot sign; it lives in the certification harness instead, which is test material,
  already signs fixture metadata, and is where `SRR-R0-L4` is *measured* rather than *held*.
* **`ho_f::f2`'s second half** — no `skip_verify` / `allow_unsigned` / `force_unsigned` / `insecure_skip` relaxation
  switch anywhere in product source outside `REFUSED_AUTHORITY_ENV`, plus the no-signing census.

**AR-0031's `c2` and `c3` still fail**, because they grep `tests/certification/srr.rs` by name for the restored text
and I did not edit that file. The properties hold — `c2b` and `c3b`, which measure them, both pass — and the checks now
run in `section6.rs`. See `evidence/HELD-OUT-FLIPS.md`.

### `AR31-N5` — see §1 and `evidence/DERIVATION.md`.

---

## 5. Bullet 6, found by the derivation

`SECTION_6_SINKS` recorded bullet 6 as `no primitive exists: Floors::raise_* are monotonic and never write a lower
value`. The derived census contradicts that by construction: **every field of `Floors` is `pub` and `save` is `pub`**,
so `f.release_high_water_sequence = 0; f.save(&ms)` is a floor-lowering primitive the mutator census could not see —
`AR31-N1`'s shape, one bullet over. No code in the product does it, and the census measures that.

`Floors::save` is now bullet 6's sink. It re-applies the persisted floors through the same monotonic `raise_*`
functions before writing, so a floor can only move up, whatever the in-memory value says and whoever set it, and the
in-memory value is updated to match so no caller is left holding a lower view. It binds **at all times**, not only
below floor: §8 says break-glass does not lower, reset or forget the floors, and ARCH-0003 §7 says the floors are the
highest values the machine has observed. Neither is conditional on the marking. Every current caller loads, raises and
saves, so the merge is a no-op for all of them — confirmed by 79 certification tests passing unchanged.

This is also a residual of `BC-R1-2` that the derivation found rather than one I was handed, and it is reported as
such.

---

## 6. Regression

Toolchain `cargo 1.98.1 (797e8a9bc 2026-08-05)`. Every run stripped of the nine refused-authority variables plus
`GOV_MACHINE_STATE_DIR`.

| Suite | Baseline at `30aa98a` | After | File |
|---|---|---|---|
| `cargo test --lib` | **36 passed, 0 failed** | **42 passed, 0 failed** | `evidence/REGRESSION-LIB.txt` |
| `cargo test --test certification` | **70 passed, 0 failed** | **79 passed, 0 failed** | `evidence/REGRESSION-CERTIFICATION.txt` |
| `cargo clippy --all-targets` | clean | clean — 0 warnings, 0 errors | `evidence/CLIPPY.txt` |

All 36 pre-existing lib tests and all 70 pre-existing certification tests still pass. The deltas are **6 new lib
tests** (4 in `srr::breakglass`, 2 in `srr::present`) and **9 new certification tests**, all in the new
`tests/certification/section6.rs`. `git diff --numstat` shows `tests/certification/srr.rs` is untouched.

## 7. The three prior held-out suites, re-run unmodified

Every `.rs` file was copied byte-identically (verified with `cmp`); only each `Cargo.toml`'s dependency path was
retargeted, by symlinking `wt/srr1-r1-verify{,-2,-3}` at this worktree — the same mechanism repair 2 used.

| Suite | on its own candidate | repair 2 | **AR-0032** |
|---|---|---|---|
| AR-0027 (`release/verification/4.1.6-r1`) | 29 / 0 | 26 / 3 | **26 passed / 3 failed** — identical |
| AR-0029 (`release/verification/4.1.6-r1-2`) | 31 / 4 | 26 / 2 of 28, `ho_f` not compiling | **26 passed / 2 failed of 28 compiled; `ho_f` does not compile** — identical |
| AR-0031 (`release/verification/4.1.6-r1-3`) | 26 / 8 | — | **27 passed / 7 failed** |

Four of AR-0031's eight failures flipped to **passing** — `hx_b::b2`, `::b3`, `::b4` (`AR31-B2`) and `hx_d::d3`
(`AR31-N1`). Three flipped from passing to **failing**, and all three are structural tripwires whose failure *is* the
repair — `hx_a::a1`, `hx_b::b6`, `hx_d::d2`. Four still fail — `hx_a::a5`, `::a8`, `hx_c::c2`, `::c3` — and all four
fail at a *location* assertion rather than at the property; each property is closed and measured, three of them by
AR-0031's own companion tests (`c2b`, `c3b`) which pass.

**Every flip is accounted for, one by one, in `evidence/HELD-OUT-FLIPS.md`.**

## 8. Preservation — re-verified after the repair (`evidence/PRESERVATION.txt`)

| Obligation | Result |
|---|---|
| `resolve_state_root` / `default_state_root` byte-identical (`AR27-OD1`, `OWNER-DECISION-0007` §1) | **BYTE-IDENTICAL**, compared function body against `30aa98a` |
| `exit_satisfied` / `EXIT_POLICY` unchanged, single exit-floor comparison (`SRR2-R1-C1`) | **BYTE-IDENTICAL**; `EXIT_POLICY = "b_stricter_both_floors"`; not widened |
| Four-operation §5 allow-list, exact match | 4 entries, unchanged; `ho_a` 6/6 (63 near misses, 0 permitted) |
| Five `admit` / five `install_kernel` sites | 5 / 5 (`hx_d::d6` passes) |
| Floors at all six ingresses, advancing last | `verifier.rs` ingress set and `staging.rs` not in the diff |
| Transaction abort not a bypass | `update.rs` rollback path not in the diff |
| D-0007 separate, establishes **intact** only | `hx_d::d8` passes |
| `SRR-R0-L4` vacuous, `gov` verifies and never signs | `hx_d::d7` passes; re-measured in `section6.rs`; only hit is the secret **detector** regex |
| `AuthenticatedRelease` sealed | 1 `by_admit` site, 1 literal; `ho_f` still does not compile |
| `Clearance` sealed, constructed nowhere outside `breakglass` | 0 sites outside |
| Contract v3 canonical import byte-identical | both `4c2df29115c8d5389034b2e2d817772add80d61678807c23e0d520c937cb5ed3` |
| Bullet 4's sink intact | `hx_a::a4`, `hx_b::b5` pass |
| `SRR-R0-L7` — offline break-glass, no first install added | `ho_b::b5` passes, `network_required = false` |
| All twelve frozen R1 items | no frozen-boundary content touched; item 9's qualification is the `AR31-B2` fix |
| No historical record touched | `release/verification/**`, `release/releases/**`, `release/root-of-trust/*-review*/**`, GATES, ESCALATION, HANDOFFS: **0 modified entries** |

## 9. Nothing stubbed. What I could not prove, and what I am reporting rather than fixing

Nothing here is stubbed, mocked or partially implemented.

**`NEW_MATERIAL_CLASS_SUSPECTED`: none.** Everything I found sits inside `BC-R1-2` (guard coverage) or `BC-R1-3`
(undetermined-subject fail-open), which `OWNER-DECISION-0008` authorises to be repaired automatically. The two items
the derivation surfaced rather than handed to me — bullet 6's latent `Floors::save` primitive (§5) and the CIT
`write_file`/`move_file` record paths (§4) — are both `BC-R1-2` residuals, both closed, both reported above rather than
absorbed silently.

**`NEW_OWNER_DECISION_REQUIRED`: none.** Everything implements a policy the owner already decided in
`OWNER-DECISION-0006` §6. No owner record, frozen-boundary content or normative source was amended.

Stated plainly, because surfacing a suspicion beats a clean-looking report:

1. **The derivation is syntactic and will not see a primitive that spells none of the product's own APIs.**
   `evidence/DERIVATION.md` §4 and §5 enumerate this and eight other limits, and name what would defeat it. The most
   likely defeat is exactly the failure mode of the three prior enumerations, made much less likely but **not
   impossible**. I make no universal claim here and the suite makes none either.
2. **Bullet 7's universality is a property of the CLI boundary.** Every `gov` command carries the marking because
   `run()` is called once and its value reaches stdout through one envelope. An **in-process embedder of
   `gov_runtime`** gets the marking only from the four surfaces that carry it in their own payload. A fifth in-process
   reporting function written tomorrow would not, and nothing in the suite would catch that.
3. **Acceptance markers are as load-bearing as signatures, and are less well defended.** A marker widened to something
   common would accept everything and nothing in the suite would notice: the positive control proves acceptance matches
   an *enforced* implementation, not that it fails to match an unenforced one. I could not find a cheap way to close
   this and am naming it rather than leaving it implicit.
4. **`records::save_record` is the record-write sink, and I did not prove it is the only writer of a governed record
   file.** The derivation finds functions that write and mention `record_path_for`/`record_dir_for`/`save_record`. A
   function that hard-codes `spec/decisions/HDG-0001.yaml` and calls `write_text` matches nothing. None exists today;
   nothing structural prevents one.
5. **`cit::take_snapshot` is the single derivation exemption**, with its reason recorded in
   `breakglass::SECTION_6_DERIVATION_EXEMPTIONS`. It computes a record's canonical path to *copy* that record into a
   rollback snapshot; it mints nothing and every byte it writes goes to the snapshot directory. I read it and believe
   the exemption; a verifier should read it too, since an exemption is the one place a wrong judgement passes quietly.
6. **A file-level grep census over product source will now also count `breakglass.rs`** for any primitive named in
   `SECTION_6_SIGNATURES`. That is a cost of naming the primitives in checkable source, and a future verifier's greps
   must exclude the table.
7. **AR-0031's `hx_a::a5` still fails and its underlying finding is closed.** `a5` looks for the bullet-2 clause to
   become an effect property *in `tests/certification/srr.rs`*; it became one in the product (`records::save_record`)
   and is tested in `tests/certification/section6.rs`. I did not edit `srr.rs`, so `a5` cannot see it. If the next
   verifier disagrees with that judgement, the remedy is to move the assertions, not to weaken them.
