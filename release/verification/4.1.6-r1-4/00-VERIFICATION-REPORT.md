# AR-0033 — fresh independent R1 verification of `srr1-r1-candidate-4`

| Field | Value |
|---|---|
| Run | AR-0033, `verifier-d`, R1 verification iteration 4. **Not AR-0027, AR-0029 or AR-0031, and not either repair role.** |
| Handoff | `release/orchestration/phase-1/HANDOFFS/HO-0033-r1-verification-4.md` (SHA-256 `ec673e5b…`) |
| Candidate | `srr1-r1-candidate-4`, structural repair work commit `cf52741` (AR-0032) |
| Worktree HEAD verified | `84b9ee8b8a34c4308f25ed12af89b90344a3bcab`, branch `phase1/srr1-r1-verify-4`, working tree clean |
| Base compared against | `30aa98a10fd7f5ed85439b0d676761080519ceed` (candidate 3) |
| Toolchain | `cargo 1.98.1 (797e8a9bc 2026-08-05)`, `rustc 1.98.1 (48a229cea 2026-09-01)` |
| Active gate | `GATE-R1-CANDIDATE-ACCEPT` |
| **Verdict** | **`ROT_PHASE1_CANDIDATE_ACCEPTED_R1`** |
| Blocking findings | **0** — `10-BLOCKING-FINDINGS.md` is present and explicitly empty |
| Materially new blocker class | **none** — no owner escalation is triggered |
| `NEW_OWNER_DECISION_REQUIRED` | none |
| `REQUIRES_R0_OR_OWNER_ADJUDICATION` | none |

I authored none of the implementation, none of the three repairs and none of the three prior verifications. I
authored my own held-out tests (`evidence/heldout-tests/`, 31 tests, 31 passing) and my own re-implementation of
the derivation mechanism, so that the thing under test is not also the thing doing the testing. No delegation:
every command in this verification was run by me.

Every digest I relied on was verified before use. All matched — `evidence/REVIEWED-CONTENT-DIGESTS.txt`. **No STOP
condition arose.**

---

## 1. The headline, stated plainly

The four-part `OWNER-DECISION-0008` mandate is met. `AR31-B1` and `AR31-B2` are closed, and I could not reopen
either. The §6 coverage claim is genuinely derived from the product rather than asserted beside it, and I proved
that non-vacuously: **the candidate's own signatures, applied to the pre-repair source, independently rediscover
all three of the items the repair says it closed** — including `AR31-B1`, which took a human verifier an entire
iteration to find. An absence claim is refutable, and no bullet claims an absence any more.

The derivation is also **much narrower than the prose around it reads**. Nine of nine plausible future primitives
I wrote go undetected. An acceptance marker does accept an unenforced implementation, and the product contained a
live example of exactly that shape one commit ago. A stdout path exists that never reaches the command-result
envelope, so the claim that `run()`'s value reaches stdout *only* through one envelope is false as written.

**None of that is a blocking R1 finding**, and I have thought hard about whether I am letting the phase finish.
The reason is the one that matters: *the candidate makes no universal claim, and at this commit no §6-forbidden
effect is reachable below floor.* `evidence/DERIVATION.md` §4 and §5 enumerate nine limits and five defeat
conditions, and **every gap I found falls inside one of them**. I verified the limits rather than accepting them,
found two of the accompanying statements inaccurate (§2.5 below), and measured that neither inaccuracy changes a
§6 verdict at this commit. §6 is a MUST NOT about what the product permits, not a requirement for a complete
static decision procedure, and nothing syntactic could supply one. The residual risk is a *future-author* risk,
which is R2 assurance, and I have recorded it as such with the precision it deserves.

---

## 2. The attack on the derivation (primary target)

### 2.1 I re-derived the census independently and got the candidate's numbers

`hv_a::a1`. I wrote my own tree walk and my own **brace-counting** function splitter — deliberately different from
the candidate's indentation splitter — and reproduced the census exactly:

```
independent walk: 84 files, 740 functions
human_gate_create                       derived 35 / writers 32 / exempt 1 / violations 0
human_gate_approve                      derived  1 / writers  1 / exempt 0 / violations 0
release_certification                   derived  2 / writers  1 / exempt 0 / violations 0
trust_policy_mutation                   derived  7 / writers  1 / exempt 0 / violations 0
privileged_plugin_acquisition           derived  9 / writers  2 / exempt 0 / violations 0
floor_lower_or_reset                    derived  3 / writers  1 / exempt 0 / violations 0
present_below_floor_release_as_current  derived  1 / writers  1 / exempt 0 / violations 0
```

**0 violations, 1 recorded exemption, independently derived.** The claimed scale (84 files, 740 functions) is
exact. A separate Python re-implementation (`evidence/DERIVATION-ATTACK.txt`) agrees line for line.

### 2.2 The mechanism is not vacuous — it rediscovers the findings by itself

`hv_a::a2`. This is the strongest evidence available either way, and it is the test I would have run first if the
repair had not suggested it. I exported `runtime/src` and `cli/src` at the **base commit** and graded them with
the **candidate's** signatures:

```
floor_lower_or_reset                    -> runtime/src/srr/state.rs::save
present_below_floor_release_as_current  -> cli/src/main.rs::main
privileged_plugin_acquisition           -> runtime/src/tools.rs::install
```

Three violations, and they are exactly `AR31-B1` (bullet 7 enforced nowhere), `AR31-N1` (the second acquisition
primitive), and the latent bullet-6 `Floors::save` primitive. **The derivation would have failed the suite on
candidate 3.** That is a real class control doing real work, and it is the single most important positive finding
in this verification.

It did **not** find the CIT `write_file`/`move_file` item: at the base commit `cit::apply_op` was accepted purely
by the `save_record(` marker. That item came from the repair author reading the code, not from the mechanism
firing — see §2.4. The repair report's phrasing "the derivation also surfaced two CIT mutation ops" overstates
what the mechanism did; the DERIVATION document's own limit 6 predicts exactly this.

### 2.3 Question 1 — **can the signatures be made to miss a primitive a plausible future author would write?**

**Yes. Nine of nine.** `hv_a::a3`. I wrote that author's code — implementations of a forbidden effect in the way
somebody who knows this product, but not this table, would plausibly write it:

| bullet | what the future author writes | detected? |
|---|---|---|
| 2 (approve) | `g.set("gate_status", Value::String("ANSWERED".into()))` | **missed** |
| 2 (approve) | `g.set("gate_status", json!(ANSWERED))` via a named constant | **missed** |
| 2 (create) | `write_yaml(&p.root.join("spec/decisions").join(format!("{id}.yaml")), …)` | **missed** |
| 3 | a manifest with `"status": "CERTIFIED"` and no `certification_status` field | **missed** |
| 4 | `ms.root.join("trust").join(format!("{role}.json"))` | **missed** |
| 5 | `p.overlay_dir().join(format!("{kind}s"))` | **missed** |
| 6 | `let mut f = Floors::load(…); f.release_high_water_sequence = 0; f.save(&ms)` | **missed** |
| 7 | a new in-process function that prints the installed release | **missed** |
| 7 | a new serve mode that prints and calls `std::process::exit(0)` | **missed** |

Every one is inside a disclosed limit (§4 items 1, 2, 8) and defeat condition 1. The most striking is bullet 6:
**the missed probe is the repair's own worked example of the latent primitive.** The repair identified
`f.release_high_water_sequence = 0; f.save(&ms)` by reading, then closed it in the *sink*, and the signature it
wrote (`floors_path(`, `join("floors")`) does not match that code. The census derives `Floors::save` itself, not
the caller.

That is the right answer architecturally and I want to be clear about why it is not a defect: `hv_a::a4` proves
the sink defends it behaviourally. The monotonic merge holds against a public-field assignment, against a
default-constructed `Floors` (the "reset" half of the bullet, and the shape a future author is likeliest to
reach for), and it keeps the floor's provenance (`minimum_secure_source_sha256`) and the metadata high-waters.
It also leaves the caller's in-memory value corrected, so nobody is left acting on a floor that is not the floor.
And it is still monotonic **upward**, so this is a floor and not a freeze.

**Disposition:** the derivation is a genuine but *narrow* detector. It catches the spellings the product already
uses, which is what makes a new author reusing those APIs get caught, and nothing more. The assurance it provides
is real and bounded, and the candidate says so in those terms. → `AR33-N1`, R2.

### 2.4 Question 2 — **does any acceptance marker accept something unenforced?**

**Yes, and the product itself contained the demonstration one commit ago.** `hv_a::a5`.

By construction: for bullet 2 the signature markers are `{save_record(, record_path_for(, record_dir_for(}` and
the acceptance markers include `save_record(`. A function whose *only* signature hit is `save_record(` is
therefore accepted by the same string that derived it. That is defensible — calling the sink *is* the enforcement
— but it means acceptance is by marker and not by reachability, so a function that calls `save_record` on one
branch and writes a record path by hand on another is waved through. I built that function and confirmed the
derivation accepts it.

Measured in the product: at the base commit, `cit::apply_op` matched the bullet-2 signature, performed a durable
write, carried **no** bullet-2 enforcement of its own, and was **accepted purely by the `save_record(` marker**
while its `write_file` branch wrote a governed record path with `write_text`. The census passed it. At the
candidate commit the instance is closed — `apply_op` now carries `guarded_record_effect(` and asks §6 twice — and
I confirmed it is the only bullet-2 writer that touches a record-path builder besides the exemption.

**Disposition:** the repair flagged this as *"as load-bearing as signatures and less defended"* and said it found
no cheap fix. That assessment is accurate, and I could not find a cheap fix either. The positive-control check
proves acceptance matches an *enforced* implementation; nothing proves it fails to match an unenforced one, and a
marker widened to something common would accept everything silently. → `AR33-N2`, R2. **This is the mechanism's
weakest joint and the condition I would prioritise.**

### 2.5 Question 3 — **does the bullet-7 marking survive a reporting path that does not go through the CLI envelope?**

**I found a path, and two accompanying claims are inaccurate.** `hv_b::b5`.

`cli/src/main.rs::run`, in the `Cmd::Capabilities { op: CapCmd::ServeEmbed … }` arm, writes its response to stdout
with `println!` and then calls `std::process::exit(0)` from **inside `run()`**. Control never reaches the
`match result` in `main()` that attaches the presentation. I drove it on a genuinely marked machine through the
real binary: the emitted JSON carries **no `release_trust` key at all**.

Two claims are therefore false as written:

1. `present.rs` and the `main.rs` comment both state that "`run()` is called exactly once and its value reaches
   stdout **only** through the match below". It does not: there is a stdout write and a process exit inside
   `run()`. It is the only one — I checked the whole of `run()` (lines 778–989) and there is exactly one
   `process::exit` and one other `println!` (the `gate present` human rendering, whose envelope still follows).
2. `evidence/DERIVATION.md` §4 limit 10 states of the two non-result print sites that "**the derivation finds
   them**; they are accounted for here rather than silently excluded". It does not find them. Both live inside
   `cli/src/main.rs::run`, and I measured that `run` matches neither bullet-7 signature marker (`"command": name`,
   `"ok": true, "command"`), so it is not in the derived set and carries no acceptance marker either. They are
   accounted for **in prose only**.

**Why this does not block.** The bypassing path reports `{"protocol": "gov-capability/1", "ok": true, "provider":
{"id": …, "version": "1"}, "outputs": …}` — a *provider protocol version*, not the installed release, and no
currency claim about it. §6 bullet 7 forbids "treating the below-floor release as current or fully trusted"; this
path makes no such statement, so the normative MUST NOT is not breached. The substance was disclosed by the
repair (§4 limit 10 names both sites and gives this exact reason); what is wrong is a sub-clause about the
mechanism's reach, not the safety argument. This is materially unlike `AR31-B1`, where the effect genuinely
occurred on four surfaces an operator reaches first.

**What worries me, and why it is R2 rather than R1:** a second serve mode written tomorrow that *did* report the
installed release would be a live bullet-7 defect, and nothing in the suite would catch it — the derivation does
not reach into `run`, and the envelope is not on that path. That is a future-author risk. → `AR33-N3`, R2, with
the claim-accuracy half recorded as `AR33-N4` (LOW, R1 lifecycle, non-blocking).

### 2.6 The nine limits in `DERIVATION.md` §4, each tested

| # | limit as stated | my finding |
|---|---|---|
| 1 | it is syntactic, not a decision procedure | **true.** `hv_a::a3`: 9/9 plausible primitives missed. Correctly stated. |
| 2 | an implementation using none of the product's primitives is invisible | **true and understated.** Even implementations that *do* use the product's primitives are missed when the spelling is computed (probes 4, 5, 6, 7 of `a3`). |
| 3 | anything outside `runtime/src` and `cli/src` is out of view | **true.** The floor assertions (>40 files, >300 functions) catch a shrinking tree, not a growing one. Confirmed by reading; no new top-level directory exists at this commit. |
| 4 | everything after the first `#[cfg(test)]` is unseen | **true, and harmless here.** `hv_a::a9`: 17 files are cut; the cut hides **zero** §6-signature-matching writers. The cut removes 53 functions (793 → 740), none §6-relevant. |
| 5 | the splitter assumes rustfmt | **true, and its stated mitigation is FALSE.** `cargo fmt --check` **fails** at this commit: 57 hunks across 8 files including `main.rs`, `breakglass.rs`, `present.rs`, `state.rs` (`evidence/RUSTFMT-CHECK.txt`). The tree is *not* rustfmt-canonical. **Measured consequence: none.** `hv_a::a8` runs both splitters over every function: they disagree on exactly one body (`runtime/src/util.rs::glob_to_regex`) and **no §6 verdict changes**. → `AR33-N5`, LOW. |
| 6 | acceptance is by marker, not by reachability | **true, and it is the live weakness.** §2.4. |
| 7 | a `&Clearance` is trusted at the boundary | **true.** `gates::build` takes the sealed witness as proof; the derivation does not re-derive that it was obtained *now*. The repair's answer — the record-write sink binds at the instant of the write — is the right one, and I verified it behaviourally (`hv_d::d1`). |
| 8 | dynamic dispatch, macros and run-time strings are invisible | **true**, and correctly compensated: `guarded_record_effect` dispatches on the type at the instant of the write, which is why AR-0031's non-literal-type construction is caught at run time though invisible to any scan (`hv_d::d1`). |
| 9 | bullet 7's universality is a property of the CLI boundary | **true**, and §2.5 sharpens it: there is also a stdout path inside the boundary that bypasses the envelope. |
| 10 | two non-result print sites in `main.rs`, "the derivation finds them" | **the second half is FALSE.** §2.5. |

### 2.7 The five defeat conditions in §5, each tested

| # | defeat condition | my finding |
|---|---|---|
| 1 | a new primitive spelling nothing the signature names | **confirmed, 9 of 9** (`hv_a::a3`). Correctly ranked as the most likely defeat. |
| 2 | a new reporting surface consumed in-process | **confirmed** (`hv_b::b7`), and extended: also a new stdout surface *inside* the CLI that exits early (§2.5). |
| 3 | widening an acceptance marker | **confirmed** (`hv_a::a5`), and the product held an example one commit ago. The stated mitigation (the lib test rejects blank markers only) is accurately described as insufficient. |
| 4 | an exemption added without the derivation finding anything | **mitigated as claimed.** The re-check is real: `hv_a::a10` confirms the suite fails on a stale exemption, on one that now carries enforcement, and on one naming a function that no longer exists. I verified all three conditions hold for the single entry. |
| 5 | deleting a positive control | **mitigated as claimed** — the test panics by name. Verified by reading `section6.rs`; the `unwrap_or_else(|| panic!(…))` is on the lookup, so removal is loud. |

### 2.8 Are the positive controls genuine?

`hv_a::a6`. **Partly. Three of seven are cosmetic, and I say so plainly.**

The mechanism around them is genuine and worth having: each control must be matched by its signature, recognised
as writing, and **not** matched by any acceptance marker, or the suite fails — so a detector cannot be silently
switched off, and that is a real answer to `AR31-N5`. The arithmetic counter-check is also real.

But a control only proves as much as the distance between it and the detector:

* **Behavioural (the control exercises a product primitive a new author must call):** `human_gate_create`
  (`record_path_for(`), `trust_policy_mutation` (`join("root.json")`), `privileged_plugin_acquisition`
  (`join("plugins")`), `floor_lower_or_reset` (`floors_path(`).
* **Cosmetic (the control is written around the literal the signature names):** `human_gate_approve`
  (`json!("ANSWERED")`), `release_certification` (`certification_status`), and most of all
  `present_below_floor_release_as_current`, whose control is a **verbatim copy of the one existing envelope
  line** with the enforcement removed. It proves the detector recognises the implementation it was derived from,
  which is the failure one level along that the handoff warned about.

And even the behavioural four are evadable: `a3` evades three of them with a computed path, and the bullet-6
control is not the primitive the repair itself identified. **Judgement: the controls establish non-vacuity, not
coverage.** The suite's own wording ("a detector that cannot flag its own positive control fails the test") is
accurate and does not overclaim; the repair report's framing — "written the way a future author plausibly would"
— is generous for three of the seven. → folded into `AR33-N1`, R2.

### 2.9 The single exemption, read

`hv_a::a10`. **I read it and I accept it.**

`runtime/src/cit/mod.rs::take_snapshot` is derived for bullet 2 because it calls `record_path_for`. I checked the
recorded reason against the code rather than against the prose:

* the computed record path is used **only** to test existence (`if !p.root.join(&pth).exists()`) and push the
  result onto `created_paths`, which exists so a CIT rollback knows what to delete. It is a **read**.
* every write destination is derived from the snapshot tree: `std::fs::copy(&src, &dst)` where
  `dst = snap.join(&rel)`, `copy_dir(&src, &snap.join(&rel))`, and `write_json(&dir.join("snapshot.json"), …)`,
  with `dir = snapshot_dir(p, id)` = `p.runtime_dir()/cit/<id>` and `snap = dir.join("snapshot")`. My test
  enumerates the write sites and asserts each targets that tree; there is no write to a record path.
* it mints no record: no `new_record`, no `save_record`, no `Record` construction.

The reason recorded in `SECTION_6_DERIVATION_EXEMPTIONS` is therefore accurate and the exemption is correct. The
anti-rot machinery around it is real, and the list is still length 1.

---

## 3. `AR31-B1` — §6 bullet 7, tested in both directions

`hv_b`, 7 tests, all passing. Below floor and above floor, in-process and through the real binary.

**A below-floor machine does not read as current** (`b1`, `b4`, `b6`). On a genuinely marked machine the sink
returns `below_floor: true`, `presented_as: BELOW_FLOOR_RECOVERY_ONLY`, the byte-exact `DEGRADED — RECOVERY ONLY`
token, bullet 7, the entry time, and an exit condition naming an authenticated release. `attach` **demotes** the
currency claim rather than sitting beside it: `up_to_date` becomes `false` and `"nothing to do"` is replaced with
text naming §6 bullet 7 — which is the right design, because the affirmative claim *is* the forbidden
presentation. Through the binary, `gov version`, `gov doctor`, `gov gate list`, `gov policy overrides`,
`gov claims list` and `gov plugins list` all carry the marking on the envelope, including the three that have no
relationship to release identity whatsoever. The human-readable (non-JSON) surface carries the banner too.

**An unmarked machine is not spuriously marked, and the marking lifts** (`b2`, `b4`). On a clean machine every
surface reports `below_floor: false`, `presented_as: CURRENT`, `marking: null`, and a true `up_to_date` survives
untouched. I then marked a machine, cleared the record the way `try_exit` does, and confirmed the marking lifts
immediately — a marking that never lifts is indistinguishable from noise, and this one lifts.

**No false-positive path from a benign environment** (`b3`). Because `presentation()` is now on *every* command's
path, a benign failure to resolve the state root would mark every healthy machine. I removed `HOME` and
`XDG_STATE_HOME` entirely: `default_state_root` falls back to the temp directory rather than erroring, and the
machine correctly reports `below_floor: false`. This was the most plausible way the new sink could have made
things worse and it does not.

**The four surfaces AR-0031 named**, re-measured: `doctor.rs` carries `release_trust` in both return paths (and
keeps `verdict` as a separate predicate, correctly — `doctor`'s own `DEGRADED` verdict already means something
else); `update::check` carries it and demotes; `gov version` is covered by the envelope; `context::compile`
carries it inside the deterministic authority block, which is right because that block is hashed and consumed as
a unit. Bullet 7 now has five call sites, four outside `breakglass.rs` (`hv_a::a7`), against zero on candidate 3.

**The bypass** is §2.5. It is the one direction the claim does not hold, it makes no currency claim, and it is
non-blocking.

---

## 4. `AR31-B2` — fail closed, and §5 restoration still works

`hv_c`, 6 tests, all passing. Both halves matter: a control that fails closed is only correct if the recovery mode
it guards can still be left.

**Fail-closed** (`c1`). On a provisioned, genuinely marked machine with `GOV_MACHINE_STATE_DIR` pointing
elsewhere — the one input the product already classifies as hostile, and the one AR-0031 showed cleared
everything — **all eight** effects and every operation label I tried now return
`SRR_BELOW_FLOOR_SUBJECT_UNDETERMINED` with `"subject": "UNDETERMINED"`, `"fail": "closed"`, the correct refusal
class, and a message naming the variable to unset. Labels that do not exist (`"an operation invented after this
verification"`, `""`) are refused identically. Bullet 7 fails closed the same way: `presented_as: UNDETERMINED`,
`below_floor: true` — unknown is not "no". The fail-open pattern is gone from the whole tree (`c6`): zero
occurrences of `resolve_state_root() else`.

**§5 restoration is not blocked** (`c2`). Under the *same* hostile input, all four `PERMITTED_OPERATIONS` clear
both `guard_light` and `guard_effect`, because the allow-list is consulted before any state read in both
functions. With no override at all, the same four are permitted and `gate create`, `release build`,
`trust root-update`, `kernel reinstall --force` and `checkpoint --all` are refused. Matching is exact: six
near-miss spellings of permitted labels are all refused. The table is still four entries and the policy is still
`allow_list_default_refuse`.

**The recovery mode can be exited** (`c3`). This is the check I cared most about, because an unexitable
break-glass would be worse than the defect being fixed. On a marked machine with real floors: an unauthenticated
release never clears; an authenticated release below the floor does not clear and reports the policy; an
authenticated release at or above **both** floors **clears the marking**, and every surface agrees immediately.
Neither new sink stands in the way — `try_exit` writes the marking record with `write_durable` and passes through
neither `save_record` nor `guard_effect`. `EXIT_POLICY` is `b_stricter_both_floors`, unchanged, and
`exit_satisfied` refuses on either floor alone.

**An unreadable marking is still exitable** (`c4`, preserving `AR29-C1`). A corrupt marking record reads as
marked by every consumer, refuses `gate create`, still permits `kernel reinstall`, and a satisfied exit still
clears it. The failure mode where the guard refuses for ever while `trust status` reports `degraded: null` does
not return.

**The state-carrying form is unaffected** (`c5`): `guard_effect_on` refuses every effect under the identical
input, because it is handed the `MachineState` and resolves nothing — which is why bullet 4 held when the others
did not.

**No §5 route is blocked by the new record-write sink.** I checked what each allow-listed operation persists:
`checkpoint` writes a `"checkpoint"` record, `gov recover` writes a `"report"` record, and `update --apply` /
`--rollback` write no records. `GUARDED_RECORD_TYPES` contains only `human-gate`, so none of them is touched.

---

## 5. The three closures the derivation found

| item | closure | verified |
|---|---|---|
| `Floors`' `pub` fields and `pub save` were a floor-lowering primitive | `Floors::save` re-applies the persisted value through the monotonic `raise_*` functions before writing, at all times, not only below floor | **Closed.** `hv_a::a4` — behavioural, four ways: public-field assignment, a default-constructed `Floors`, provenance retention, and upward monotonicity preserved. The in-memory value is corrected too. §8 and ARCH-0003 §7 both bind unconditionally, so making it unconditional is right. |
| CIT `write_file` / `move_file` reached a governed record path without `save_record` | both parse their content and ask §6 by the record type the bytes declare | **Closed.** `hv_d::d2` — exactly two `guarded_record_effect(` and two `guard_effect(effect,` calls in `apply_op`, named `cit write_file` and `cit move_file`; `append_record` still persists through the sink rather than growing a second control. |
| `gov gate present` reached no `guard_write` and mutated a Human Gate record below floor | refused at the record-write sink | **Closed.** `hv_d::d3` — `gates::present` has no `guard_write`, calls `save_record(&p.root, g)`, and **refuses any record whose type is not `human-gate` before the write**, so the type-keyed dispatch necessarily fires. Combined with `hv_d::d1`'s behavioural proof that `save_record` refuses a `human-gate` write below floor, the chain from command to refusal is closed. `gate present` is not on the §5 allow-list, so the refusal is not an accident of the operation table. |

**Is the mechanism finding these evidence for or against the derivation working?** My call: **for**, and
substantially — but for a narrower proposition than the repair's prose implies. §2.2 settles it: run the
candidate's signatures against the pre-repair tree and **all three** appear, including a HIGH finding that cost a
full iteration to discover by hand. That is a class control doing work no enumeration did in three attempts. The
qualification is that the CIT item was *not* found this way — `apply_op` was accepted by a marker (§2.4) — so the
repair's "the derivation also surfaced two CIT mutation ops" credits the mechanism with a find that came from
reading. The mechanism's own document predicts exactly that outcome in limit 6, which is to its credit.

---

## 6. Residual dispositions

| residual | disposition |
|---|---|
| `AR31-N1` | **Closed.** `hv_d::d4`: `tools::install` calls `plugins::guard_acquisition_below_floor`, which asks `Effect::PrivilegedPluginAcquisition`; refused below floor with the class named. The derived census finds **both** capability-registry writers (`tools.rs::install`, `capabilities/governance.rs::register`) and requires the enforcement in each. `tools install` keeps its operation-level guard as well. |
| `AR31-N2` | **Closed.** `hv_d::d4`, behavioural: a capability declaring `required_permission_classes: ["READ_ONLY"]` **and** one declaring nothing at all are both refused below floor. With comments stripped, no descriptor read precedes the guard; `let privileged = is_privileged(descriptor);` now comes after it. Above floor nothing changes. The routing rationale (ARCH-0003 §9 — deciding whether to *ask* is a form of authorising) is correct. |
| `AR31-N3` | **Closed.** `hv_d::d1`, behavioural: all three of AR-0031's constructions — literal type, computed type, and retyping an existing record via `Record::set` — persist above floor and are all refused below floor at `records::save_record` with `refused_class: human_gate_create`, `section_6_bullet: 2`. An unguarded type (`task`) is unaffected, so this is a §6 control and not a freeze. The `&Clearance` on `gates::build` is kept; the two bind different things and both are present. |
| `AR31-N4` | **Closed, with a standing concern I am recording rather than grading.** `hv_d::d5` reproduces **both** properties in held-out material from an independent S+L malleation: a malleated signature is refused by `crypto::verify` and `crypto::verify_strict` with the same error code (and a flipped byte fails too, so the result is not passing for an unrelated reason), and no relaxation switch appears in product source outside `REFUSED_AUTHORITY_ENV`. Both also run durably in `tests/certification/section6.rs`. **On the migration question:** `SRR-R0-L4` binds the *shipped product*, and the census that measures it walks only `runtime/src` and `cli/src`, so a signing capability in `tests/` does not breach it — and `tests/certification/` already signs fixture metadata. The restoration is faithful, not weakened: the assertions are the same strength as `ho_f::f1`'s. My concern is structural, not technical — this is the second time a check has migrated into the implementer's own suite, and independence is a property of who writes the check, not of whether it runs. → `AR33-N6`, R2. |
| `AR31-N5` | **Closed.** `hv_a::a7`: no `SECTION_6_SINKS` entry begins `"no primitive"`; every §6 activity has a signature; `SECTION_6_SIGNATURES.len() == REFUSED_ACTIVITIES.len()`. The dedicated test fails outright on any absence claim, a signature deriving nothing panics by name, and every bullet has a positive control the detector demonstrably flags. The exact inversion of `AR31-N5`. |

**Observation, not a finding — bullet 6 has no `guard_effect` call site.** `Effect::FloorLowerOrReset` is declared
and reportable but asked nowhere outside `breakglass.rs`, which is the surface shape of `AR31-B1`. It is **not**
the same defect: bullet 6 is enforced by making the effect structurally impossible at the only writer, which is
stronger than refusing it, and I verified that behaviourally (`hv_a::a4`). Bullet 7's defect was that it was
enforced by *nothing* while an untrue claim excused it. AR-0031's own `hx_a::a7`, which asserts bullet 6 has no
call site outside `breakglass.rs`, still passes.

**Observation — an unreported second instance of a reported behaviour change.** `status::continue_work` calls
`gates::present` for the first pending gate, so `gov continue` on a marked machine with a pending gate is now
refused at the record-write sink, exactly as `gov gate present` is. The repair enumerated only `gov gate present`.
The refusal is **correct** — mutating a Human Gate record below floor is precisely §6 bullet 2, and `continue` is
not a §5 recovery activity — but an operator meets it without warning. → `AR33-N7`, R2 (documentation).

---

## 7. Owner-closed items — verified, not graded

`OWNER-DECISION-0007` §1 / `AR27-OD1` and `SRR2-R1-C1`. `hv_c::c6` extracts each function body from the candidate
and from the base commit and compares:

* `resolve_state_root` — **byte-identical**
* `default_state_root` — **byte-identical**
* `exit_satisfied` — **byte-identical**
* `EXIT_POLICY` — `"b_stricter_both_floors"`, unchanged; not widened

…despite `state.rs` and `breakglass.rs` both being edited. Machine-state path resolution derives from
`XDG_STATE_HOME`/`HOME` as the owner decided, still refuses `GOV_MACHINE_STATE_DIR` on a provisioned machine
(`SRR_PROTECTED_STATE_OVERRIDE_REFUSED`), and still honours it on an unprovisioned one (ARCH-0003 §8 CI-runner
route — verified live). Only the *handling of the error* changed, which is the `AR31-B2` fix. **Confirmed
independently. Not graded.**

`SRR-R0-L7` (`hv_d::d8`): the break-glass module contains no network primitive of any kind, and `authorise` reads
the local inbox only. No offline first install was added. Recovery works with no network.

---

## 8. Item-by-item disposition of the frozen R1 section

Frozen boundary SHA-256 `70977d11b778c4a8391a65cb3e0f53103bcc1e565de595c1e83150797f1699c1`, verified.

| # | frozen R1 item | disposition | basis |
|---|---|---|---|
| 1 | a mature reviewed TUF/cryptographic implementation is used correctly | **HOLDS** | `hv_d::d5` independent S+L malleability; `ed25519-dalek` strict verification; AR-0027 `heldout_srr`/`srr4` 16/16, AR-0029 `ho_d`/`ho_e` 11/11 |
| 2 | candidate/source files cannot create their own trusted identity | **HOLDS** | `hv_d::d7` — one `AuthenticatedRelease` construction, one `by_admit`, zero `Clearance` constructions outside `breakglass`; AR-0029 `ho_f` still does not compile against the sealed type |
| 3 | wrong keys, modified metadata/payload/migration, replay, downgrade, expiry fail closed | **HOLDS** | AR-0027 and AR-0029 reruns unchanged; `hv_d::d5`; `hv_a::a4` monotonic floors (downgrade) |
| 4 | all privileged ingress paths call the common verifier | **HOLDS** | `hv_d::d7` — five `admit` sites paired with five `install_kernel` sites; `verifier.rs`/`staging.rs` not in the diff |
| 5 | verified bytes staged, installed and used without substitution | **HOLDS** | unchanged by this repair; AR-0027 `heldout_srr` passes |
| 6 | staging/install/rollback/recovery atomic and crash-safe | **HOLDS** | `write_durable` unchanged; transaction abort path not in the diff; 79 certification tests including failure injection |
| 7 | metadata/release high-water durable and monotonic | **STRENGTHENED** | `hv_a::a4` — monotonicity moved from the callers into `Floors::save`, so it now binds code that has not been written |
| 8 | post-install integrity distinct; D-0007 controls effective | **HOLDS** | `hv_d::d7` — `kernel_trust.rs` establishes **intact** and never speaks of authenticity or admissibility; AR-0031 `hx_d::d8` passes |
| 9 | project, CLI, environment, model and plugin inputs cannot create trust or approval | **HOLDS — and item 9's `AR31-B2` qualification is discharged** | `hv_c::c1` — the environment variable that cleared all eight effects now refuses all eight; `hv_d::d4` — a plugin descriptor can no longer decide whether §6 is asked |
| 10 | CI/multi-machine provisioning follows ARCH-0003 | **HOLDS** | `hv_c::c6` — the CI-runner override still works on an unprovisioned machine, still refused on a provisioned one |
| 11 | original product controls, Gate W and G0–G6 mappings remain valid | **HOLDS** | 42 lib + 79 certification tests pass, zero failures; `tests/certification/srr.rs` untouched |
| 12 | builder evidence and fresh independently authored held-out evidence pin the exact candidate | **HOLDS** | this run: 31 held-out tests authored against `84b9ee8`, 31 passing; three prior suites rerun unmodified at their claimed figures |

---

## 9. The seven AR-0031 failures — my independent verdict on each

I reproduced AR-0031's suite byte-identically (`cmp` verified) and got **27 passed / 7 failed**, exactly the
claimed figure and exactly the claimed seven tests. For each: *is the property still held, and is it still tested
somewhere durable?*

| test | why it fails now | property held? | tested durably? | my verdict |
|---|---|---|---|---|
| `hx_a::a1` | asserts the set of bullets claiming "no primitive" is still `["floor_lower_or_reset", "present_below_floor_release_as_current"]`; it is now `[]` | **yes — this is the repair** | `section6.rs::a_no_primitive_claim_is_refutable_by_this_suite` fails on any absence claim; `hv_a::a7` re-measures | **Structural tripwire on the old shape. The failure IS the repair.** Agreed with the repair's account. |
| `hx_a::a5` | final assertion greps `tests/certification/srr.rs` for `record_dir_for("human-gate")` / `save_record` / `Record::set`; the property moved to `records::save_record` + `section6.rs` | **yes — and stronger than a5 asked for** | `section6.rs::a_human_gate_record_cannot_be_written_below_floor_however_it_was_minted`; `hv_d::d1` proves all three constructions behaviourally | **Location assertion. Property closed.** The repair's account is accurate. |
| `hx_a::a8` | asserts the bullet-7 sink string still reads `"no primitive: every reporting surface carries the marking"`; it now names the real sink | **yes — this is the repair** | `section6.rs` bullet-7 tests; `hv_b` 7 tests | **Structural tripwire. The failure IS the repair.** The repair grouped a8 with the "location assertion" set; it is really the same class as `a1` — a claim-string tripwire. Immaterial mislabel, correct substance. |
| `hx_b::b6` | asserts the fail-open appears in exactly 2 places; it now appears in 0 | **yes — this is the repair** | `section6.rs::an_undetermined_subject_fails_closed_at_both_enforcement_points`; `hv_c::c1`, `c6` | **Structural tripwire. The failure IS the repair.** Agreed. |
| `hx_c::c2` | unconditional `panic!` unless `srr.rs::the_no_bypass_and_no_signing_preservation_census_still_holds` contains `verify_strict(` and `malleat`; the restoration went to `section6.rs` | **yes** | `section6.rs::the_dropped_held_out_sub_checks_run_here`; **and AR-0031's own `c2b` passes**; and `hv_d::d5` reproduces it independently | **Location assertion. Property closed and now tested in three places.** Note AR-0031's companion `c2b` — which measures the property rather than its location — **passes at this commit**, which is independent confirmation from the complaining verifier's own suite. |
| `hx_c::c3` | same shape, for the relaxation-switch census | **yes** | `section6.rs`; **AR-0031's own `c3b` passes**; `hv_d::d5` re-derives it over product source | **Location assertion. Property closed.** Same reasoning. |
| `hx_d::d2` | asserts as a *baseline* that an unprivileged remote capability is not a §6 bullet 5 effect; it now is | **yes — this is the repair** (`AR31-N2`) | `section6.rs::both_capability_acquisition_primitives_ask_section_6_without_consulting_the_descriptor`; `hv_d::d4` behaviourally | **Structural tripwire on the old behaviour. The failure IS the repair.** Agreed. |

**Verdict on the account:** accurate. Four failures are structural tripwires asserting the old shape (`a1`, `a8`,
`b6`, `d2` — the repair said three and put `a8` in the other bucket, which is a labelling detail, not a
substantive error), and three are location assertions against a file the repair deliberately did not edit (`a5`,
`c2`, `c3`). **No regression is hiding behind the story.** The strongest independent evidence is that AR-0031's
own companion tests `c2b` and `c3b`, which measure the properties rather than their location, both pass — and I
reproduced both properties a third time in held-out material.

I agree with the repair's remedy statement: if a future verifier disputes where the assertions live, the answer is
to move them, not to weaken them.

---

## 10. Prior held-out suites — rerun, none edited

Every `.rs` file copied and `cmp`-verified byte-identical against the committed evidence; only each `Cargo.toml`'s
dependency path was retargeted by symlink. Run with `--test-threads=1` (the harnesses set process-wide
environment; running them in parallel races and produces spurious failures, which I confirmed before settling on
the serial figures).

| suite | claimed | **measured by me** | failing tests |
|---|---|---|---|
| AR-0027 (`4.1.6-r1`) | 26 / 3 | **26 passed / 3 failed** ✓ | `b1`, `b2`, `d3` — identical to the repair's evidence |
| AR-0029 (`4.1.6-r1-2`) | 26 / 2 of 28, `ho_f` not compiling | **26 passed / 2 failed of 28 compiled; `ho_f_preservation` does not compile** ✓ | `b3`, `b6` — identical. The compile failure is `cannot construct AuthenticatedRelease with struct literal syntax due to private fields`, i.e. `AR29-N1` closing. |
| AR-0031 (`4.1.6-r1-3`) | 27 / 7 | **27 passed / 7 failed** ✓ | `a1`, `a5`, `a8`, `b6`, `c2`, `c3`, `d2` — identical |

All three figures and all twelve failing-test identities reproduce exactly.

---

## 11. Regression, reproduced independently

| suite | repair's figure | orchestrator | **AR-0033** |
|---|---|---|---|
| `cargo test --lib` | 42 passed, 0 failed | 42 passed | **42 passed; 0 failed; 0 ignored** |
| `cargo test --test certification` | 79 passed, 0 failed | 79 passed | **79 passed; 0 failed; 0 ignored** |
| my held-out suite | — | — | **31 passed; 0 failed** |

`evidence/REGRESSION.txt`, `evidence/HELD-OUT-TEST-OUTPUT.txt`. `git diff --numstat 30aa98a HEAD` confirms
`tests/certification/srr.rs` is **not** in the diff, and no product test was edited or weakened.

`cargo fmt --check` **fails** (57 hunks, 8 files) — recorded as `AR33-N5` with its measured consequence (none).

---

## 12. Classification, and why the owner is not being interrupted

**Blocking findings: 0.** **Materially new blocker classes: 0.**

I considered escalation seriously, because under `OWNER-DECISION-0008` a single new class stops the loop, and
because three iterations in a row have surfaced a class underneath the one that was closed. The candidate for a
fourth class would be *"the coverage mechanism's own coverage is unmeasured"* — the derivation cannot detect what
it cannot spell, which §2.3 demonstrates nine times over.

**I do not call that a new class, and here is my reasoning rather than a label.**

* It is not a new *mechanism* of failure. `BC-R1-2` is guard coverage — an effect reaching no enforcement point.
  What I measured is the residual tail of exactly that, one level up: the *detector* for guard coverage is
  itself incomplete. Viewing a known class at meta-level does not make it a new class.
* It produces **no reachable counterexample at this commit**. I derived the census independently and found zero
  violations; I tested each bullet's sink behaviourally and every one refuses. The gap is a future-author risk.
* Decisively: **it is disclosed, bounded and correctly ranked by the candidate itself.** `DERIVATION.md` §4 and
  §5 name every gap I found, and §5 ranks "a new primitive that spells nothing the signature names" as the single
  most likely defeat. The repair states "I make no universal claim here and the suite makes none either". A
  finding cannot falsify a claim that was never made, and I will not manufacture a blocker out of a limitation
  the candidate volunteered.
* The three prior new classes each required rethinking the control's shape. This one has a known and stated
  shape, and the honest answer to it — that no syntactic mechanism is a decision procedure — is not something an
  owner decision can change.

The two claims I did falsify (§2.5, and limit 5's rustfmt mitigation) are **sub-clauses of the mechanism's
self-description with no §6 consequence at this commit**, measured as such rather than asserted. Promoting a
documentation inaccuracy to an R1 blocker would be inflating a residual to look rigorous, which the handoff
warns against as explicitly as it warns against the opposite. I have recorded both precisely, at LOW, in
`20-LATER-LIFECYCLE-CONDITIONS.md`, so the owner can see exactly what I weighed and overrule me if they read it
differently.

**Carried R2 items not raised here:** `AR31-N6`, `AR29-N2`, `AR27-N3`, `AR27-N5`, `AR27-N6`, `AR27-N7`. I note
without grading that `AR31-N6`'s operator-facing half is now closed — `gov continue`'s envelope carries the
marking even though `status::continue_work` still forwards only `next_action` from the report it computes.

---

## 13. Scope

No product source, frozen boundary content, owner record, prior review or verification evidence,
`release/releases/**` or historical record was modified. `release/verification/4.1.6-r1-4/` is the sole new
directory. No fixes were implemented. No session or agent transcripts or task-output stores were read. No user
auto-memory was opened or written. The product owner was not contacted. **No delegation: I ran every command in
this verification myself.**

No scope deviation. No STOP condition.
