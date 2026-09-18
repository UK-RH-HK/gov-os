# AR-0033 — non-blocking conditions

Seven conditions. None blocks `GATE-R1-CANDIDATE-ACCEPT`. Each states its normative source, provenance class,
lifecycle, whether it falsifies a claim or proposes stronger assurance, consequence, evidence, and
residual-versus-materially-new.

**All seven are residuals within known classes. None is a materially new class. None requires an owner decision
or a boundary change.**

---

## R1 lifecycle — true of the candidate, non-blocking, no reachable §6 counterexample

### `AR33-N4` — two claims about the bullet-7 mechanism's reach are false as written

| Field | Value |
|---|---|
| Severity | **LOW** |
| Normative source | none breached. The claims are the candidate's own, in `runtime/src/srr/present.rs`, the `cli/src/main.rs::main` comment, and `evidence/DERIVATION.md` §4 limit 10 |
| Provenance class | **falsifies a claim** — two sub-clauses of the mechanism's self-description |
| Lifecycle | R1 (accuracy of the candidate's own evidence), non-blocking |
| Classification | **Residual** of `BC-R1-2` |
| Evidence | `hv_b::b5` |

Claim 1: "`run()` is called exactly once and its value reaches stdout **only** through the match below." It does
not. `cli/src/main.rs::run`, in the `CapCmd::ServeEmbed` arm, writes to stdout with `println!` and then calls
`std::process::exit(0)`, so `main()`'s envelope is never reached. Driven on a marked machine through the real
binary, the emitted JSON carries no `release_trust` key.

Claim 2: `DERIVATION.md` §4 limit 10 says of the two non-result print sites that "**the derivation finds them**;
they are accounted for here rather than silently excluded". It does not find them. Both sit inside
`cli/src/main.rs::run`, which matches neither bullet-7 signature marker (`"command": name`,
`"ok": true, "command"`), so `run` is not in the derived set and carries no acceptance marker either. They are
accounted for in prose only.

**Consequence: none at this commit.** The bypassing path emits a provider protocol version, not the installed
release, and makes no currency claim, so §6 bullet 7 is not breached. Recorded because the universality argument
is load-bearing rhetoric for this repair and both statements should be corrected to match what the code does.

**Proposed correction (not implemented — this run implements nothing):** state the property as "every *command
result* reaches stdout through one envelope; `serve-embed` is a protocol responder that exits before it and
reports no release identity", and delete the "the derivation finds them" clause or make it true by widening the
bullet-7 signature to reach `run`.

### `AR33-N5` — the splitter's rustfmt assumption has no mitigation, because the tree is not rustfmt-canonical

| Field | Value |
|---|---|
| Severity | **LOW** |
| Normative source | none breached. `evidence/DERIVATION.md` §4 limit 5 |
| Provenance class | **falsifies a claim** — the limit's stated mitigation |
| Lifecycle | R1, non-blocking |
| Classification | **Residual** of `BC-R1-2` |
| Evidence | `evidence/RUSTFMT-CHECK.txt`, `hv_a::a8` |

`section6.rs::split_functions` closes a function at the first line equal to its opening indent plus `}`, which is
sound only on canonically formatted code. Limit 5 acknowledges this and offers "`cargo clippy --all-targets` is
clean and the tree is rustfmt-canonical at this commit" as the mitigation. **`cargo fmt --check` fails**: 57
hunks across 8 files, including `cli/src/main.rs`, `runtime/src/srr/breakglass.rs`, `runtime/src/srr/present.rs`
and `runtime/src/srr/state.rs`.

**Consequence: none at this commit, measured rather than assumed.** I ran a brace-counting splitter and the
candidate's indentation splitter over all 740 functions: they disagree on exactly one body
(`runtime/src/util.rs::glob_to_regex`) and **no §6 verdict changes for any bullet**. The limit is real but
currently costs nothing.

**Stronger assurance:** either enforce formatting in CI so the mitigation becomes true, or make the splitter
brace-based so the assumption disappears. The second is a dozen lines and removes the limit rather than
documenting it.

---

## R2 lifecycle — assurance strength, not defects in this candidate

### `AR33-N1` — the derived census is a narrow detector; 9 of 9 plausible future primitives evade it

| Field | Value |
|---|---|
| Severity | **MEDIUM** (assurance) |
| Normative source | `OWNER-DECISION-0006` §6 — satisfied at this commit. This proposes stronger assurance; it falsifies nothing, because the candidate declines the universal claim |
| Provenance class | **proposes stronger assurance** |
| Lifecycle | **R2** |
| Classification | **Residual** of `BC-R1-2` — the same coverage class observed at the detector rather than at the guard |
| Evidence | `hv_a::a3`, `evidence/DERIVATION-ATTACK.txt` §3 |

Nine implementations of forbidden effects, each written as somebody who knows this product but not this table
would plausibly write it, are **all** missed: a gate approval spelled with `Value::String` or a named constant; a
gate file written at a hand-built path; a certification manifest with a differently spelled status field; a trust
role file with a computed name; a capability registry with a computed directory; **the repair's own worked
example of the latent bullet-6 primitive** (`f.release_high_water_sequence = 0; f.save(&ms)`); a new in-process
reporting surface; a new serve mode that prints and exits.

Every one is inside `DERIVATION.md` §4 limits 1, 2 and 8 and §5 defeat condition 1, which ranks it as the single
most likely defeat. **No §6 effect is reachable below floor at this commit** — the census derives 0 violations
independently and each bullet's sink refuses behaviourally, including the bullet-6 case the census cannot see
(`hv_a::a4`). This is a future-author risk.

Related: **three of seven positive controls are cosmetic** — `human_gate_approve`, `release_certification` and
especially `present_below_floor_release_as_current`, whose control is a verbatim copy of the one existing
envelope line with the enforcement removed. The mechanism around the controls is genuine (a detector that cannot
flag its control fails the suite, and none fires on arithmetic) and establishes **non-vacuity**, but three
controls prove only that the detector recognises its own spelling. `hv_a::a6`.

**Stronger assurance, in descending value:** (a) make each bullet's positive control an *independently written*
implementation rather than one built around the marker — the cheapest change with the most signal; (b) add a
second control per bullet that the signature must **also** catch, so a control cannot be co-designed with its
detector; (c) prefer type- or path-level chokepoints over string markers where the product allows it, as bullets
2 and 6 already do.

### `AR33-N2` — acceptance markers accept unenforced implementations, and the product held an example

| Field | Value |
|---|---|
| Severity | **MEDIUM** (assurance) — **the mechanism's weakest joint** |
| Normative source | `OWNER-DECISION-0006` §6 — satisfied at this commit |
| Provenance class | **proposes stronger assurance**; confirms the repair's own stated uncertainty 3 |
| Lifecycle | **R2** |
| Classification | **Residual** of `BC-R1-2` |
| Evidence | `hv_a::a5` |

Acceptance is by marker, not by reachability (`DERIVATION.md` §4 limit 6, §5 defeat 3). For bullet 2 the
acceptance marker `save_record(` is also a *signature* marker, so a function derived through it is accepted by the
same string. A function that calls the sink on one branch and writes a record path by hand on another is waved
through — I constructed one and confirmed the derivation accepts it.

**This was live in the product one commit ago.** At `30aa98a`, `cit::apply_op` matched bullet 2's signature,
wrote durably, carried no bullet-2 enforcement, and was accepted purely by the `save_record(` marker while its
`write_file` branch wrote a governed record path with `write_text`. The census passed it; the repair closed it by
reading the code. The instance is closed at this commit and no other bullet-2 writer has that shape.

The repair states this candidly and says it found no cheap fix. I agree it is not cheap: the positive control
proves acceptance matches an *enforced* implementation, not that it fails to match an unenforced one, and a
marker widened to something common would accept everything silently with nothing in the suite noticing.

**Stronger assurance:** (a) a **negative control per acceptance set** — a synthetic implementation carrying the
marker but not the enforcement, which the suite must still report as a violation; this is the direct inverse of
the positive control and closes the stated gap; (b) where a marker is both signature and acceptance (bullet 2's
`save_record(`), require the *write* to be reachable only through the sink, e.g. by making the record-path
builders private to `records.rs`; (c) reject acceptance markers shorter than a threshold or shared across bullets.

### `AR33-N3` — bullet 7's universality does not extend past the CLI envelope

| Field | Value |
|---|---|
| Severity | **LOW–MEDIUM** (assurance) |
| Normative source | `OWNER-DECISION-0006` §6 bullet 7 — satisfied at this commit |
| Provenance class | **proposes stronger assurance** |
| Lifecycle | **R2** |
| Classification | **Residual** of `BC-R1-2` |
| Evidence | `hv_b::b5`, `hv_b::b7` |

Two routes escape the envelope: an **in-process embedder** of `gov_runtime` (disclosed as limit 9 — it gets the
marking only from `doctor::run`, `update::check`, `context::compile`, `status::status` and `recovery::recover`,
which carry it in their own payload), and a **stdout writer inside `run()` that exits before the envelope**
(`AR33-N4`). Neither reports the installed release today. A fifth in-process reporting function, or a second serve
mode that *did* report it, would be a live bullet-7 defect with nothing in the suite to catch it: the derivation
does not reach `run`, and the envelope is not on either path.

**Stronger assurance:** (a) widen the bullet-7 signature so that any function in `cli/src` performing a durable
write **and** mentioning `FRAMEWORK_VERSION` / `framework_version()` is derived — that catches both routes; (b)
route the two non-result print sites through a tiny helper that calls `present::attach`, so "prints to stdout"
and "carries the marking" become the same act; (c) treat `p.framework_version()` as a bullet-7 signature marker
in `runtime/src` as well, so an in-process reporting surface is derived at the point it reads the version.

### `AR33-N6` — a second held-out check has migrated into the implementer's own suite

| Field | Value |
|---|---|
| Severity | **LOW** (process/assurance independence) |
| Normative source | none breached. `SRR-R0-L4` is intact and vacuous |
| Provenance class | **proposes stronger assurance** |
| Lifecycle | **R2** |
| Classification | **Residual** of `AR31-N4` |
| Evidence | `hv_d::d5` |

`AR31-N4` is genuinely closed: `tests/certification/section6.rs::the_dropped_held_out_sub_checks_run_here`
restores both sub-checks at full strength, and I reproduced both properties independently — a malleated S+L
signature is refused by `crypto::verify` and `crypto::verify_strict` with the same error code (a flipped byte
fails too, so the result is not passing for an unrelated reason), and no relaxation switch appears in product
source outside `REFUSED_AUTHORITY_ENV`.

**On whether the move weakened it: it did not, technically.** AR-0031's stated objection was that the check
cannot live in the product suite under `SRR-R0-L4`. That objection does not hold as stated: `SRR-R0-L4` binds the
*shipped product*, the census that measures it walks only `runtime/src` and `cli/src`, and `tests/certification/`
already signs fixture metadata. The assertions are the same strength as `ho_f::f1`'s.

**The standing concern is structural, not technical.** This is the second migration of a held-out check into the
suite maintained by the role being checked, and independence is a property of who authors a check, not of whether
it runs. Nothing prevents a future repair from adjusting an assertion it also owns.

**Stronger assurance:** keep a small, permanently held-out preservation suite — owned by the verification
lineage, rerun unmodified each iteration, never editable by a repair role — as the durable home for exactly these
checks. The three prior suites already function this way in practice; making it explicit would remove the
question.

### `AR33-N7` — a second command is affected by the reported `gate present` behaviour change, unreported

| Field | Value |
|---|---|
| Severity | **LOW** (documentation) |
| Normative source | `OWNER-DECISION-0006` §6 bullet 2 — the behaviour is **correct** |
| Provenance class | **proposes stronger assurance** (completeness of a disclosed behaviour change) |
| Lifecycle | **R2** |
| Classification | **Residual** of `AR31-N3` |
| Evidence | `runtime/src/status.rs::continue_work`, `runtime/src/orchestration/gates.rs::present` |

`status::continue_work` calls `gates::present` for the first pending gate, which mutates a `human-gate` record and
now reaches the record-write sink. So `gov continue` on a marked machine with a pending gate is refused with
`SRR_BELOW_FLOOR_REFUSED`, exactly as `gov gate present` is. The repair enumerated only `gov gate present`.

The refusal is **right** — mutating a Human Gate record below floor is precisely what §6 bullet 2 forbids, and
`continue` is not a §5 recovery activity, so no recovery route is blocked (verified: `hv_c::c2`, `c3`). But an
operator below floor meets it without warning.

**Stronger assurance:** enumerate the reachability consequences of the record-write sink in `BELOW_FLOOR_LIMITS`
alongside `update --apply`, so an operator reads the limit at the moment it bites, as that table already does for
gate creation.

---

## Carried from prior runs, not raised here

`AR31-N6`, `AR29-N2`, `AR27-N3`, `AR27-N5`, `AR27-N6`, `AR27-N7` are R2-lifecycle and out of scope for this cycle
per the handoff. Noted without grading: `AR31-N6`'s operator-facing half is now closed, because `gov continue`'s
command-result envelope carries the marking even though `status::continue_work` still forwards only
`st["next_action"]` and discards the `release_trust` object `status::status` computed one function above. The
data-flow omission itself is unchanged.

Prior-suite failures reproduced unchanged and previously dispositioned as non-blocking: AR-0027 `b1`, `b2`
(RFC3339 expiry comparison) and `d3` (a tripwire on the pre-repair refusal surface); AR-0029 `b3`, `b6`.
