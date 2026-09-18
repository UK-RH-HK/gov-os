# AR-0029 — non-blocking conditions, by lifecycle

Everything here is recorded and routed. Nothing here blocks `GATE-R1-CANDIDATE-ACCEPT` on its own.

---

## R1 lifecycle — cheap, local, and belongs in the same repair cycle as the blockers

### `AR29-C1` — LOW — an unreadable marking record can be entered but not exited

| Field | Value |
|---|---|
| Normative source | `OWNER-DECISION-0006` §7 as supplemented by `OWNER-DECISION-0007` §2: "Normal governed operation resumes only after an authenticated release at or above [both floors] is installed and verified" |
| Provenance class | `NECESSARY-DERIVED` (the §7 obligation), reported against an `IMPLEMENTATION-CHOICE` the repair made |
| Lifecycle | R1 implementation |
| Falsifies a claim? | **Yes** — `breakglass.rs` `Marking::Unreadable` states "Recovery is unaffected … so the exit path stays open". The restore half is true; the exit half is false. |
| Convergence label | **RESIDUAL of `AR27-B1`** — `Marking::Unreadable` is new in repair 1 and the claim about it is new in repair 1 |

**What happens.** Two readers of `degraded/<product>.json` disagree:

| reader | used by | an unreadable record means |
|---|---|---|
| `read_marking` (new in repair 1) | `guard`, `guard_light` | **marked** → refuse everything off the allow-list |
| `Degraded::load` (unchanged) | `try_exit`, `is_degraded`, `gov trust status`, `gov trust break-glass`, `gov recover` | **not marked** → `Ok(None)`, write nothing |

So after restoring an authenticated release at or above both floors — the §7 exit condition — `record_installed`
calls `try_exit`, which returns `None`, rewrites nothing, and the guard keeps refusing. Measured
(`ho_c_deadlock.rs::c3`):

```text
AR-0029 C3 — after installing an authenticated release above BOTH floors:
  try_exit returned None
  marking record rewritten = false
  `cit approve` still refused = true
  is_degraded() reports = false   (the guard disagrees)
```

And the machine tells the operator the opposite of what it enforces (`::c4`):

```text
AR-0029 C4 — `gov trust status`.degraded = null; `gov trust break-glass`.currently_degraded = false;
             guard_light("cit approve") = SRR_BELOW_FLOOR_REFUSED
```

**Why LOW and not blocking.** Reachability is the deciding factor and it is low: `write_durable` is
temp → fsync → rename → fsync(dir), so no crash produces a partial record, and no writer in the product emits a
record without a boolean `active`. Reaching this state needs external corruption, an I/O error, or a
hand-edited protected file. When it does happen the refusal is self-describing — `details.break_glass_record
.unreadable_marking_record` names the exact path — and the remedy (removing that file) is available to the owner,
who `ARCH-0003` §1 places inside the trusted boundary. It is a wrong state an operator can diagnose and leave,
not a brick. Verified across seven corruption shapes (`::c1`), all refusing, all naming the file.

**Recommendation.** Make the two readers agree. Either `Degraded::load` should treat an unreadable record the
same way `read_marking` does, so `try_exit` can overwrite it on a satisfied exit, or `try_exit` should clear an
unreadable record when `exit_satisfied` holds for an authenticated release. Either is a few lines in the file
already being repaired.

### `AR29-N4` — LOW — an allow-listed restoration route cannot complete when a Human Gate is required

Second limb of `AR29-B2`. `update --apply` is one of the four §5 entries, but when `human_gate_required` is true
(always for a non-`CERTIFIED` target) it returns `HUMAN_GATE_REQUIRED`, and answering that gate is — correctly,
per §6 bullet 2 — refused below floor. The allow-list therefore promises an operation the rest of the system
will not let finish.

Not a deadlock: `kernel reinstall` and `update --rollback` are gate-free and were verified reachable below floor
(`ho_b_coverage.rs::b5`). Whether `update --apply` should stay on the allow-list, or the recovery path should be
exempted from the update gate, is a design decision for the repair role; either way the allow-list and the
reachable behaviour should agree.

### `AR29-N5` — INFO — `REFUSAL_CLASSES` names operations that do not exist

Of its 17 entries, `trust revoke`, `policy set`, `plugin install`, `plugin acquire`, `skills install`,
`release certify`, `certify` and `floor` correspond to no CLI command or `guard_write` label in the candidate.
Harmless in itself — the table decides nothing, exactly as the repair says — but it creates an impression of
coverage that a label sweep reads as enforcement. That is precisely how AR-0027's `d3` produced a false negative
on `trust root-update`. Worth a comment saying the table is aspirational-and-inert, or pruning it to what exists.

### `AR29-N1` — INFO — "constructible only by `admit`" is an enumeration property, not a type property

Every field of `AuthenticatedRelease`, `Staged`, `MachineState` and `Floors` is `pub`, and none of the four has a
private field. A struct literal therefore compiles from any crate that depends on `gov-runtime` —
`ho_f_preservation.rs::f4` **is** that struct literal, and it builds an `AuthenticatedRelease` claiming
`Authenticity::Authentic` at sequence 9999 from outside the product.

The property that genuinely holds, and which I verify, is the enumerated one: `install_kernel` takes
`&AuthenticatedRelease` and has no path-taking variant, there are exactly five `admit` sites and exactly five
`install_kernel` call sites, and each of the five is paired. No ingress can install from a source directory by
mistake. Fabricating a value requires writing new product or caller source, which is what the five/five census
inspects.

**Non-blocking**, but AR-0027's wording ("`AuthenticatedRelease` has no public constructor") and the repair
report's preservation row ("constructible only by `admit`") overstate it, and the architecture leans on the
phrase "compiler-enforced". Either add one private field (a zero-sized `admitted: Admitted` token) and the claim
becomes true as written, or restate it as the census property it is.

### `AR29-N3` — INFO — two spellings of the marking path

`guard_light` builds `degraded/{product.replace(['/','\\'], "_")}.json`; `MachineState::degraded_path` uses
`safe()`, which maps everything outside `[A-Za-z0-9._-]` to `_`. For `FRAMEWORK_NAME =
"agentic-engineering-os"` both produce the same name, so there is no live divergence. A product string
containing a space or any other non-`safe` character would make the hot-path guard read a different file from the
one `enter` wrote — a silent total bypass of §6 at the main chokepoint. One line: have `guard_light` resolve
through `MachineState::at(root)` and `degraded_path`.

---

## R2 lifecycle

### `AR29-N2` — INFO — the canonical-timestamp gate is syntactic, not calendrical

`is_canonical_utc_timestamp` validates digit positions, not ranges. `9999-99-99T99:99:99Z` passes and reads as a
future expiry; `0000-00-00T00:00:00Z` passes and reads as expired (`ho_d_expiry.rs::d4`). Not adversary-reachable
— `expires` is inside the signed byte-string — and lexicographic ordering stays sound, so the direction of any
error is a publisher's own. A publisher-side lint or a `chrono` parse would close it. R2, with `AR27-N3`.

### Carried unchanged from AR-0027, not re-examined this cycle

`AR27-N3` (timestamp/snapshot roles optional; currency not required for trust-changing ingresses),
`AR27-N5` (a case where a floor fails to rise), `AR27-N6` (`guard_acquisition` called with a hard-coded empty
delegation slice), `AR27-N7` (capability evidence population). All R2, all carried per `HO-0029`.

---

## Owner-decided, verified but not graded

- **`SRR2-R1-C1` / break-glass exit** — `OWNER-DECISION-0007` §2 closed this as owner policy. Verified still at
  the single point `breakglass::exit_satisfied` with `EXIT_POLICY = "b_stricter_both_floors"`, and that nothing
  else in the codebase compares a release against an exit floor. The policy itself is not graded.
- **`AR27-OD1` / machine-state anchoring** — `OWNER-DECISION-0007` §1 closed this. Not raised, not probed as a
  defect, and no repair role may change path resolution on its account.
- **`SRR-R0-L7`** — stays absent by owner decision. Break-glass recovery remains local-only: `authorise` reads
  the protected inbox, the trusted root and the local clock, and `gov trust break-glass` reports
  `requirements.network_required = false` (asserted in `ho_b_coverage.rs::b5`).

## `NEW_OWNER_DECISION_REQUIRED`

**None.** Both blocking findings implement a policy the owner has already decided in `OWNER-DECISION-0006` §6.
Nothing in this verification requires a new owner decision, and nothing is marked
`REQUIRES_R0_OR_OWNER_ADJUDICATION`.
