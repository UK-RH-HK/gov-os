# AR-0031 — non-blocking conditions

None of these blocks `GATE-R1-CANDIDATE-ACCEPT`. Each states its lifecycle. None requires an owner decision.

## R1 conditions — true of the candidate, but no reachable counterexample follows

### `AR31-N1` — the §6 bullet 5 census entry names one sink for a bullet the product realises in two places

*Normative source:* `breakglass::SECTION_6_SINKS`, the candidate's own claim. *Provenance:* falsifies that claim.
*Lifecycle:* R1. *Classification:* **residual** of `AR29-B1`/`B2` (an effect reaching no *effect-level*
enforcement point). *Evidence:* `hx_d::d3`.

`tools::install` installs a capability — including one declaring `SYSTEM_INSTALL`, `SECRET_READ` or
`DEPLOY_PRODUCTION` — and never calls `plugins::guard_acquisition`, which the census names as the sole sink for
bullet 5. The sink has exactly one caller, `capabilities::governance::register_plugin`.

*Why non-blocking:* below floor `tools install` is refused by `guard_write(p, "tools install")` → the allow-list
default-refuse, with `refused_class = privileged_plugin_acquisition`. The §6 property holds at that door today. What
does not hold is the *class control* claimed for this bullet: the coverage is operation-level, which is the
arrangement repair 2 itself argued is insufficient because it depends on whoever writes the next capability-
installing function remembering. A future acquisition path that takes no `Project` would reach neither control.

*Condition:* before R2, either route `tools::install` through the sink or amend the census entry to name both
primitives, so the table states what the product does.

### `AR31-N2` — whether §6 bullet 5 is consulted at all is decided by the descriptor

*Normative source:* ARCH-0003 §9, "descriptors cannot self-authorise". *Provenance:* proposes stronger assurance.
*Lifecycle:* R1. *Classification:* new observation, non-blocking. *Evidence:* `hx_d::d2`.

`plugins::guard_acquisition` calls `guard_effect` only `if is_privileged(descriptor)`, and `is_privileged` reads
`required_permission_classes` straight out of the descriptor. The module's stated principle — that a descriptor
cannot move a capability into a weaker class — is true of the `Acquisition` class, which is derived from where the
bytes are, and is *not* true of the privileged/unprivileged split that gates the §6 check. A descriptor declaring
`READ_ONLY`, or declaring nothing, never reaches the check even below floor and even when remotely acquired.

*Why non-blocking:* this is defensible on its face — §6 bullet 5 names *privileged* acquisition, so an
unprivileged one is not the forbidden effect. It is recorded because it is the only §6 sink whose decision to ask
is taken on self-asserted data; bullets 2, 3 and 4 ask unconditionally. The residual risk is that the
declared classes and the capability's actual behaviour can diverge.

### `AR31-N3` — the bullet 2 census clause is a source-literal property, not the effect property it is described as

*Normative source:* `breakglass::SECTION_6_SINKS` and `gates::build`'s doc comment. *Provenance:* falsifies the
stated strength of a claim. *Lifecycle:* R1. *Classification:* **residual** of `AR29-B2`. *Evidence:* `hx_a::a5`,
`hx_d::d4`.

`gates::build` is described as putting the enforcement point on the path by compiler action. That is true for new
functions written **inside `gates.rs`**, because `build` is private and takes a sealed `&Clearance`. It is not true
of the product as a whole: `records::new_record`, `records::save_record` and every field of `Record` are `pub` and
take no clearance. I minted a `human-gate` record three ways with no `Clearance` in existence — a non-literal type
argument, `Record::set("type", …)` on an existing record, and the public constructor.

The certification test that polices this clause (`section_6_effects_are_enforced_inside_their_sinks`, A6) greps for
the source literal `new_record("human-gate"` and asserts it occurs once. None of the three constructions above
spells that literal.

*Why non-blocking:* the literal does occur exactly once, so **no second path exists in the product today**. The
finding is that the test cannot see one if it is added.

*Condition:* before R2, police the clause by the effect — e.g. assert that `record_dir_for("human-gate")` is
reached only from `gates.rs`, or that no `save_record` call outside `gates.rs` can carry that type — rather than by
one source literal.

### `AR31-N4` — two sub-checks were lost when `ho_f`'s preservation census moved into the product suite

*Normative source:* frozen R1 item 12 (held-out evidence pins the candidate). *Provenance:* assurance coverage.
*Lifecycle:* R1. *Classification:* new observation, non-blocking. *Evidence:* `hx_c::c1`–`c3b`.

`ho_f_preservation` no longer compiles — correctly, because its `f4` is the literal `AR29-N1` asked to be made
impossible. Its other checks were reproduced in the product suite as
`the_no_bypass_and_no_signing_preservation_census_still_holds`. Compared assertion by assertion, the migration is
faithful for `f3`, `f5` and `f7`, **strengthens** `f1`'s static half (`ho_f` printed the bare-`.verify(` census;
the migrated test asserts it empty), and drops two sub-checks:

1. **`f1`'s behavioural half** — a malleated S+L signature must be refused by both `crypto::verify` and
   `crypto::verify_strict` with the same error code. The product suite cannot sign, so it cannot reproduce this.
   Since `ho_f` no longer compiles, the check now runs nowhere in the candidate's evidence.
2. **`f2`'s second half** — no `skip_verify` / `allow_unsigned` / `force_unsigned` relaxation switch anywhere in
   product source outside `REFUSED_AUTHORITY_ENV`. `grep -rn` over `tests/` finds none of these strings.

**Both underlying properties still hold.** I measured both directly (`hx_c::c2b`, `hx_c::c3b`), so this is a loss
of assurance coverage, not a live defect. `f6` (Contract v3 byte-identity) is not in the migrated census but is
independently covered by a pre-existing certification test at `tests/certification/srr.rs:967`, and I verified it
myself (`hx_d::d9`).

*Condition:* before R2, either keep a signing-capable held-out crate in the evidence set for the malleability
check, or add the relaxation-switch census to the product suite where it costs nothing. The first cannot live in
the product suite by design (`SRR-R0-L4`: `gov` must not be able to sign), which is exactly why the check belongs
in held-out evidence.

### `AR31-N5` — the census test cannot fail on the two bullets that claim no primitive exists

*Normative source:* the candidate's own test. *Provenance:* proposes stronger assurance. *Lifecycle:* R1.
*Classification:* supporting observation behind `AR31-B1`. *Evidence:* read directly from
`tests/certification/srr.rs`.

`section_6_effects_are_enforced_inside_their_sinks`'s A2 loop iterates a hard-coded list of the five sinks that
name a function. The two entries whose sink string begins `"no primitive:"` are silently skipped, and A1 only
checks the table's shape. The unit test `every_section_6_activity_has_exactly_one_declared_sink` asserts only that
each sink string is non-empty. So the bullet 6 and bullet 7 claims are unfalsifiable by the candidate's own suite.
Bullet 6's claim happens to be true; bullet 7's is not, which is `AR31-B1`.

## R2 conditions

### `AR31-N6` — `gov continue` drops the release-trust block its own callee computes

*Lifecycle:* R2 (reporting completeness). `status::continue_work` calls `status(p)` and forwards only
`st["next_action"]`, discarding the `release_trust` object — including the marking — that `status::status`
computed one function above. Related to `AR31-B1` but listed separately because it is a data-flow omission in a
surface that *does* have the marking available, rather than a surface with no awareness of it.

## Carried from prior runs, not raised here

`AR29-N2`, `AR27-N3`, `AR27-N5`, `AR27-N6`, `AR27-N7` are R2-lifecycle and out of scope for this cycle per the
handoff.
