# AR-0032 — the derivation mechanism: what it does, what it can and cannot see, and what would defeat it

`OWNER-DECISION-0008` mandate parts 3 and 4. This is the part of the repair that is meant to end the pattern, so it
is written to be disagreed with precisely.

## 1. The problem it replaces

`OWNER-DECISION-0006` §6 is a **universal negative**: "while marked `DEGRADED — RECOVERY ONLY`, the product MUST NOT
permit X". It was implemented three times as a **positive enumeration**:

| iteration | the enumeration | how it went short |
|---|---|---|
| 1 | the list of forbidden **operations** (26 substrings) | anything unlisted proceeded |
| 2 | the set of guarded **call sites** | anything reaching no call site was unenforced |
| 3 | the census of **effect primitives** (`SECTION_6_SINKS`) | a bullet whose primitive was *asserted not to exist* was enforced nowhere |

Each was complete and correct when written. Each went silently short the moment the product grew a path its author had
not enumerated. And at every level **the test was derived from the same enumeration as the code**, so it could not
detect that the enumeration was short: AR-0027's sweep pushed operation *labels* through the guard, and AR-0031 found
the same shape one level down (`AR31-N5`) — the census test's loop skipped exactly the bullets whose entry said
"no primitive".

## 2. What is derived now

The certification test `section_6_coverage_is_derived_from_the_product`
(`tests/certification/section6.rs`) does this, in order:

1. **Enumerate the product.** Walk every `.rs` file under `runtime/src` and `cli/src`, cut each file at its
   `#[cfg(test)]` boundary, and split what remains into functions by indentation. Measured at this commit: **84 files,
   740 functions.** The test refuses to run on fewer than 40 files or 300 functions, so a broken walk fails loudly
   instead of passing vacuously. **Nothing is on a list of places to look.** The function set is the tree.

2. **For each §6 effect, derive the set of functions that could realise it.** A function is *derived* when it matches
   the effect's **signature** and *performs a durable write*.
   - the **signature** (`breakglass::SECTION_6_SIGNATURES`) names the product's own primitives for that effect: the
     record-path builders, the protected-state path builders, the capability registries, the command-result envelope.
   - "performs a durable write" is itself derived, from `breakglass::SECTION_6_WRITE_PRIMITIVES` — the product's own
     persistence calls (`write_durable`, `write_yaml`, `write_text`, `write_json`, `save_record`, `std::fs::write`,
     `File::create`, `rename`, `.save(`, `write_all`, `println!`, `print!`).

3. **Require each derived writer to carry the enforcement.** A derived writer is accepted when it contains one of the
   effect's **acceptance markers**: the `Effect::` variant, or a call to the sink that asks it. Anything else fails the
   test **by name**: "these functions perform a durable write and match the effect's signature, and carry no
   enforcement and no call to its sink — they are second implementations of a forbidden effect".

4. **Prove the detector is not vacuous, before believing anything it says.** Each signature is first run against a
   **positive control**: a synthetic implementation of that effect, with no enforcement, written the way a future
   author plausibly would, using the product's own APIs. It must be matched by the signature, recognised as writing,
   and reported as a violation. A signature that cannot flag its own positive control **fails the test**, whatever it
   then finds in the product. The same controls are run against arithmetic, which must be flagged for nothing: a
   detector that fires on everything is as useless as one that fires on nothing.

5. **Refuse to pass silently on an empty derivation.** If a signature matches nothing at all, the test panics and says
   so, rather than quietly counting zero violations. That is the direct answer to `AR31-N5`.

Measured census at this commit (printed by the test):

```
human_gate_create:                       derived 35 / writers 32 / exempt 1 / violations 0
human_gate_approve:                      derived  1 / writers  1 / exempt 0 / violations 0
release_certification:                   derived  2 / writers  1 / exempt 0 / violations 0
trust_policy_mutation:                   derived  7 / writers  1 / exempt 0 / violations 0
privileged_plugin_acquisition:           derived  9 / writers  2 / exempt 0 / violations 0
floor_lower_or_reset:                    derived  3 / writers  1 / exempt 0 / violations 0
present_below_floor_release_as_current:  derived  1 / writers  1 / exempt 0 / violations 0
bullet 1 guard_write call sites: 27
```

## 3. How a "no primitive exists" claim can now fail

No bullet claims an absence any more — bullets 6 and 7 both have real sinks. The mechanism is kept and tested, because
the next bullet that needs one should not have to re-invent it, and because the claim's *testability* is the mandate,
not its current absence.

Three things now stand between an absence claim and the suite passing:

1. `a_no_primitive_claim_is_refutable_by_this_suite` **fails outright** on any `SECTION_6_SINKS` entry beginning
   `"no primitive"`, and its failure message says what to assert instead: that the signature derives nothing **and**
   that its positive control is still flagged.
2. Every bullet, absence-claiming or not, must have a positive control the detector demonstrably flags. An absence
   claim backed by a detector that cannot detect is worth nothing, and the suite says so in those terms.
3. A signature that derives nothing panics with "the signature for X matches nothing in the product", so an absence
   arrived at by a stale signature is not mistaken for an absence in the product.

The concrete regression this closes: on candidate 3, `Effect::PresentBelowFloorReleaseAsCurrent` had **no call site
anywhere in the product outside `breakglass.rs`**, and no test in the product's own suite could fail on that. It has
five now, and `a_no_primitive_claim_is_refutable_by_this_suite` asserts at least four exist and prints them:
`cli/src/main.rs::main`, `runtime/src/context/mod.rs::compile`, `runtime/src/doctor.rs::run`,
`runtime/src/srr/present.rs::presentation`, `runtime/src/update.rs::check`.

## 4. What the derivation **cannot** see

Stated plainly. Three prior roles in this lineage overstated a universal property and every overstatement was later
falsified by a verifier; an honest limit is worth more than a claim that reads well.

1. **It is syntactic.** It is not a decision procedure for "does this code realise this effect", and nothing syntactic
   could be. It finds code that *mentions* the product's own primitives for an effect and *writes something*.
2. **An implementation that uses none of the product's primitives is invisible.** A function that builds
   `~/.local/state/governance-os/machine/trust/root.json` by string concatenation and calls `std::fs::write` matches no
   marker for bullet 4. The path-literal markers (`join("root.json")`, `join("provisioned.json")`, `join("floors")`,
   `join("plugins")`, `join("tools")`) catch the obvious spellings. **Nothing catches a computed one.**
3. **Anything outside `runtime/src` and `cli/src` is out of view** — build scripts, future crates, anything shelled out
   to. The walk asserts a floor on the file and function count, so a *shrinking* tree is caught; a tree that grows a
   new directory is not, until someone adds it to the walk.
4. **Test modules are cut.** Everything after the first `#[cfg(test)]` in a file is not examined. A §6 primitive
   written below that line in a product file is invisible to the derivation. It would still be refused at run time by
   the sinks, but the census would not see it.
5. **The function splitter assumes rustfmt.** It closes a function at the first line equal to the opening indent plus
   `}`. Code that is not canonically formatted can merge or truncate function bodies, which could hide a violation
   inside a neighbouring accepted function. `cargo clippy --all-targets` is clean and the tree is rustfmt-canonical at
   this commit, but nothing in the suite *enforces* formatting.
6. **Acceptance is by marker, not by reachability.** A function containing `save_record(` is accepted for bullet 2
   because `save_record` asks §6 — but the derivation does not prove that call is on the path that performs the write.
   A function that calls `save_record` on one branch and writes a record path by hand on another is accepted.
7. **A `&Clearance` is trusted at the boundary.** `gates::build` takes the sealed witness as proof the question was
   asked. The derivation does not re-derive that the clearance was obtained *now* rather than earlier.
8. **Dynamic dispatch, macros and run-time strings are invisible.** A record type assembled at run time is caught by
   the *sink* (`records::save_record` dispatches on the type at the instant of the write, which is exactly why the
   bullet-2 control was moved there) but not by the census.
9. **The marking's universality is a property of the CLI boundary, not of the library.** Every `gov` command result
   carries the §6 bullet 7 presentation because `run()` is called once and its value reaches stdout only through one
   envelope. An **in-process embedder of `gov_runtime`** that calls `status::status`, `doctor::run` or
   `context::compile` directly gets the marking only because those four surfaces carry it in their own payload. A
   fifth in-process reporting function written tomorrow would not.
10. **Two non-result print sites exist in `cli/src/main.rs`** and are not command results: the human rendering of a
    Human Gate (whose machine-readable form goes through the envelope) and the `gov-capability/1` provider response
    (which reports a provider protocol version, not the installed release). The derivation finds them; they are
    accounted for here rather than silently excluded.

## 5. What would **defeat** it

The short list, in descending likelihood:

1. **A new primitive that spells nothing the signature names.** The single most likely defeat. Mitigated only by the
   signatures being about the product's own APIs, which a new author is overwhelmingly likely to reuse — and not at all
   by anything stronger.
2. **A new reporting surface consumed in-process rather than through `gov`.** Bullet 7's universality would not extend
   to it.
3. **Widening an acceptance marker.** Acceptance markers are as load-bearing as signatures. A marker widened to
   something common (`"guard"`, `"Effect"`) would accept everything, and **nothing in the suite would notice**: the
   positive-control check tests that acceptance matches an enforced implementation, not that it *fails* to match an
   unenforced one. The lib test `every_section_6_bullet_has_a_derivation_signature_and_none_claims_an_absence` rejects
   blank markers only.
4. **An exemption added without the derivation having found anything.** Mitigated: `SECTION_6_DERIVATION_EXEMPTIONS`
   entries are re-checked every run — an entry whose function no longer matches its signature, no longer writes, or now
   carries the enforcement **fails the test**. So an exemption cannot rot into a blanket. It can still be added
   deliberately and wrongly, with a plausible reason; that is a review question, not a test question.
5. **Deleting the positive control for a bullet.** The test panics with "has no positive control: an absence claim for
   it would be unfalsifiable, which is AR31-N5". So this is loud, not silent.
6. **Moving a primitive below a `#[cfg(test)]` line, or into a new top-level directory.** Both make it invisible.

## 6. A cost of the mechanism, stated so it is not mistaken for a defect

`SECTION_6_SIGNATURES` is a table of string literals that **name the product's own primitives**. A *file-level* grep
census — "which files mention `root_metadata_path`, `guard_acquisition`, `floors_path`?" — will therefore now also
count `runtime/src/srr/breakglass.rs`. A verifier writing such a census must exclude the table. The derived census
itself is unaffected: it examines function bodies, and these are module-level constants inside none.

This is visible in AR-0031's re-run: `hx_a::a6`'s bullet-5 file census briefly counted `breakglass.rs` during
development. It does not at this commit, but the interaction is real and a future grep will meet it.

## 7. Where the bullet-1 clause differs, and why

§6 bullet 1 names a **class of operations** ("normal privileged Governance OS operation"), not an effect. "Is the
enforcement inside every primitive that can realise the effect?" has no counterpart for it: the set of "privileged
governed operations" is not syntactically derivable, and trying was `AR27-B1`. Bullet 1 is decided at the operation
level by a **default-refuse allow-list**, which is a class control because it refuses everything not on a four-entry
list — including operations nobody has written yet. The derivation's contribution there is narrower and is asserted
separately: the chokepoint still routes to the guard, the call-site census has not collapsed (27 sites), the policy is
still `allow_list_default_refuse`, and near-miss labels are still refused.

**An operation that reaches no chokepoint at all is still not visible to bullet 1's clause.** That was `AR29-B1`/`B2`,
and the answer to it is not bullet 1 — it is that bullets 2–7 are enforced inside the effects, which is what everything
above measures.
