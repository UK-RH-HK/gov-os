# AR-0032 — the three prior held-out suites, flip by flip

All three suites were copied **byte-identically** (verified with `cmp` against
`release/verification/*/evidence/heldout-tests/`). Only each `Cargo.toml`'s dependency path target changed, by
symlinking `wt/srr1-r1-verify`, `wt/srr1-r1-verify-2` and `wt/srr1-r1-verify-3` at this worktree — the mechanism
repair 2 used and documented. No `.rs` file was edited.

Raw output: `AR-0027-HELD-OUT-RERUN.txt`, `AR-0029-HELD-OUT-RERUN.txt`, `AR-0031-HELD-OUT-RERUN.txt`.

---

## AR-0027 (`release/verification/4.1.6-r1/evidence/heldout-tests`) — **26 passed / 3 failed**, expected, identical to repair 2

| file | AR-0027 on candidate 1 | repair 1 | repair 2 | **AR-0032** |
|---|---|---|---|---|
| `heldout_srr` | 12 / 0 | 12 / 0 | 12 / 0 | **12 / 0** |
| `heldout_srr2` | 8 / 0 | 6 / 2 | 6 / 2 | **6 / 2** |
| `heldout_srr3` | 5 / 0 | 4 / 1 | 4 / 1 | **4 / 1** |
| `heldout_srr4` | 4 / 0 | 4 / 0 | 4 / 0 | **4 / 0** |

The three failures are `heldout_srr2::b1`, `::b2` (`AR27-N1`) and `heldout_srr3::d3` (`AR27-B1`) — the same three
`OBSERVED:` weakness assertions repair 1 closed. **No change from repair 2**, which is the point: repair 1's closure
of `BC-R1-1` is intact and nothing in this repair disturbed it.

---

## AR-0029 (`release/verification/4.1.6-r1-2/evidence/heldout-tests`) — **26 passed / 2 failed of 28 compiled; `ho_f` does not compile**, expected, identical to repair 2

| file | AR-0029 on candidate 2 | repair 2 | **AR-0032** |
|---|---|---|---|
| `ho_a_allowlist` | 6 / 0 | 6 / 0 | **6 / 0** |
| `ho_b_coverage` | 4 / 2 | 4 / 2 | **4 / 2** |
| `ho_c_deadlock` | 3 / 2 | 5 / 0 | **5 / 0** |
| `ho_d_expiry` | 5 / 0 | 5 / 0 | **5 / 0** |
| `ho_e_rootexpiry` | 6 / 0 | 6 / 0 | **6 / 0** |
| `ho_f_preservation` | 7 / 0 | does not compile | **does not compile** |

`ho_b::b3` and `::b6` remain the two structural tripwires repair 2 flipped: both assert the *absence* of a guard and
both now correctly fail. `ho_f_preservation` still fails to compile with `cannot construct AuthenticatedRelease with
struct literal syntax due to private fields` — its `f4` **is** the literal `AR29-N1` asked to be made impossible, so
that is the finding closing, not a regression. Its other six checks are covered by
`srr.rs::the_no_bypass_and_no_signing_preservation_census_still_holds`, and the two sub-checks that census dropped are
restored in `section6.rs::the_dropped_held_out_sub_checks_run_here` (`AR31-N4`).

**No change from repair 2.**

---

## AR-0031 (`release/verification/4.1.6-r1-3/evidence/heldout-tests`) — **27 passed / 7 failed** (baseline 26 / 8)

| file | AR-0031 on candidate 3 | **AR-0032** |
|---|---|---|
| `hx_a_census` | 6 / 2 | **5 / 3** |
| `hx_b_failopen` | 3 / 3 | **5 / 1** |
| `hx_c_prior_evidence` | 6 / 2 | **6 / 2** |
| `hx_d_acquisition_and_preservation` | 11 / 1 | **11 / 1** |
| total | **26 / 8** | **27 / 7** |

### Flipped to PASSING — 4. All four are `OBSERVED:` findings closing.

| test | finding | why it now passes |
|---|---|---|
| `hx_b::b2` | `AR31-B2` | `GOV_MACHINE_STATE_DIR` on a provisioned, marked machine no longer clears any of the eight §6 effects. `guard_effect` returns `SRR_BELOW_FLOOR_SUBJECT_UNDETERMINED`, so the test's `permitted` list is empty |
| `hx_b::b3` | `AR31-B2` | same at the operation-level point: `guard_light` refuses every one of the seven labels the test tries |
| `hx_b::b4` | `AR31-B2` | `gates::create_system`'s only §6 control no longer issues a `Clearance` under the override, so no Human Gate is created below floor and none becomes approvable |
| `hx_d::d3` | `AR31-N1` | `tools::install`'s body now contains `crate::srr::plugins::guard_acquisition_below_floor("tools install")`, the named §6 door in the acquisition module, which asks `guard_effect(Effect::PrivilegedPluginAcquisition, …)` |

`hx_b::b1` passed on candidate 3 as well (its grep for the justification comment matched nothing, because the comment
was line-wrapped). It still passes, and now for the substantive reason: the comment it objected to is gone.

### Flipped to FAILING — 3. All three are structural derivation checks, not properties. Each failure **is** the repair.

| test | assertion that fails | why it is the repair |
|---|---|---|
| `hx_a::a1` | "the set of bullets claiming no primitive changed": expected `["floor_lower_or_reset", "present_below_floor_release_as_current"]`, found `[]` | **Both claims are gone.** Bullet 7 has a real sink (`srr::present::presentation`) — that is `AR31-B1`. Bullet 6 has a real sink (`Floors::save`, monotonic against the persisted value) — the derived census found the latent `pub` field + `pub save` primitive the mutator census could not see. `a1` pins the old shape; the old shape was the defect |
| `hx_b::b6` | `bg_rs.matches("let Ok(root) = crate::srr::state::resolve_state_root() else {").count()` — expected 2, found 0 | **The fail-open pattern is gone from `breakglass.rs`.** `b6`'s own message says "expected the fail-open in exactly `guard_light` and `guard_effect`". Its other assertions still hold and are re-asserted by `section6.rs`: `resolve_state_root` has exactly one `Err(` and it is the override refusal, `default_state_root` still derives from `XDG_STATE_HOME`/`HOME`, and the pattern appears in no other file. `b6` also greps for the source string `AR27-OD1 is out of scope`, which is now written with backticks round the identifier — a wording change, not a scope change |
| `hx_d::d2` | `guard_acquisition` body contains `"if privileged {"` — no longer true | **`AR31-N2` is closed.** The §6 question is asked unconditionally; `is_privileged` still reads the descriptor but only to *report* the class, never to decide whether to ask. `d2`'s own title is "the descriptor decides whether §6 is consulted at all" — it no longer does |

`hx_a::a6` ("no second primitive realises a named §6 effect") **passes**. During development it briefly failed because
`SECTION_6_SIGNATURES` named `guard_acquisition(` as a string literal and `a6` counts files mentioning it; the marker
was widened past the call syntax for an independent reason and the interaction went away. It is recorded in
`DERIVATION.md` §6 because the general hazard is real: a file-level grep census must exclude the signature table.

### Still failing — 4. All four fail at a **location** assertion; the property each is about is closed and measured.

| test | what it asserts | where the property is now |
|---|---|---|
| `hx_a::a5` | `OBSERVED` (`AR31-N3`): "the bullet-2 census clause is a source-literal property". Its condition is that `tests/certification/srr.rs` contains `record_dir_for("human-gate")`, `save_record` or `Record::set` | The clause is now an **effect** property in the product: `records::save_record` asks §6 by record type (`breakglass::GUARDED_RECORD_TYPES`), so all three of `a5`'s own constructions are refused however the record was minted. Tested in `section6.rs::a_human_gate_record_cannot_be_written_below_floor_however_it_was_minted` and in the lib test `a_guarded_record_type_is_recognised_however_the_record_was_minted`. `a5` greps `srr.rs` by name and I did not edit `srr.rs`, so it cannot see it |
| `hx_a::a8` | Fails at its **first** assertion, `assert_eq!(claim, "no primitive: every reporting surface carries the marking")`, which pins the old census string. That assertion runs before its four `OBSERVED:` ones | The census entry is now `crate::srr::present::presentation — …`, which is `AR31-B1` closing. **All four of `a8`'s `OBSERVED:` conditions were verified individually and now hold**: `doctor.rs` references the marking (it did not, at all); `update::check`'s body references it; `context/mod.rs` references `below_floor`; and `Effect::PresentBelowFloorReleaseAsCurrent` has call sites outside `breakglass.rs` — five, in `present.rs`, `main.rs`, `doctor.rs`, `update.rs` and `context/mod.rs` |
| `hx_c::c2` | `OBSERVED` (`AR31-N4`): the migrated census in `srr.rs` must contain `verify_strict(` and `malleat` | Restored in `section6.rs::the_dropped_held_out_sub_checks_run_here`, which performs the S+L malleation and asserts both entry points refuse with the same code. AR-0031's own `c2b`, which **measures** the property, passes |
| `hx_c::c3` | `OBSERVED` (`AR31-N4`): the migrated census must contain `skip_verify` or `allow_unsigned` | Restored in the same test, widened to `skip_verify`, `skip-verify`, `allow_unsigned`, `allow-unsigned`, `force_unsigned`, `insecure_skip`, with the no-signing census beside it. AR-0031's own `c3b`, which measures the property, passes |

For `a5`, `c2` and `c3` the remedy available to me without editing a pre-existing test was to put the restored
coverage in a new module. If the next verifier judges that the coverage belongs in `srr.rs` where AR-0031 looked for
it, moving the assertions there is a mechanical change; **nothing about it would weaken an assertion**, which is why I
left the judgement open rather than pre-empting it.
