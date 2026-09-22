# OWNER-DECISION-P2-0007 — A + C: remove the architectural pattern, not another enumeration

| Field | Value |
|---|---|
| Record | Owner decision (product owner, 2026-09-22) |
| Id | **OD-P2-07** |
| Status | IN FORCE for Phase 2 |
| Answers | `PHASE_2_ARCHITECTURE_REVIEW_PACKAGE.md`, the escalation OA-P2-06's stop condition produced after P2-AR-0077 |
| Authorises | continuation **beyond** OA-P2-06's previous stop condition |
| Supersedes | nothing; OD-P2-03, OC-P2-04 and OD-P2-05 all stand, and this settles *how* their requirements are met on this surface |

## The decision

**A + C, as one bounded structural architecture remediation.** In the owner's words:

> Do NOT treat this as another local enumeration/patch round. The purpose is to remove the architectural pattern
> responsible for the repeated failures, then subject the result to fresh independent attack before any candidate is
> minted.

`cap2-candidate-2` must not be minted until the conditions in §7–§10 below are satisfied.

## A — no raw or unbound command may acquire ungated installation authority

Four rounds established that predicting arbitrary raw-command semantics through program lists, argument lists, flag
lists, path-token parsing, wrapper detection or special command shapes **does not provide a complete trust boundary**.
That strategy stops here.

For an installation to proceed through the **ungated trusted path**, the executable artefact must be explicitly
identified and cryptographically bound to the authority that reviewed it:

```
reviewed descriptor
      ↓
exact installation artefact identity
      ↓
digest / content binding
      ↓
pre-execution byte verification
      ↓
exact bound artefact executes
```

If execution cannot be reduced to an exact bound artefact whose bytes are verified immediately before execution, it is
**undetermined** and requires the appropriate gate.

Raw/unbound execution includes, unless reduced to a verified artefact: direct `curl …`, direct `cp …`, arbitrary shell
expressions, interpreter expressions, package-manager command expressions, opaque build commands, dynamically
constructed command lines, and **command semantics that depend on external argument/config files not contained in the
reviewed bound artefact**.

> **The architecture property: no raw or unbound command may acquire ungated installation authority.**

**Explicitly forbidden as a fix for AR77-F1/F2/F4**: adding another curl flag, another command shape, another program,
another path syntax, or another parser exception.

A raw command may still execute **through an appropriate governed gate** where policy allows. Ordinary conforming
acquisition is preserved by letting projects wrap installation logic in a pinned reviewed artefact — an installation
script whose exact bytes are bound and re-verified before execution.

The security review must bind to the specific descriptor/version, the installation artefact/bundle identity, its
digest(s), and any executable artefact the installation requires. **A subjectless or artefact-less review must not
manufacture installation authority.**

## C — one authoritative source for `class` authority semantics

AR77-F3 showed authority-bearing `class` semantics duplicated across consumers, with the repair comparing two of six
values and one of two consumers. **Do not fix this by adding the four missing values to another list.**

Establish one authoritative predicate answering:

> **Does this class confer any exemption from any governed control?**

Every relevant consumer derives its authority semantics from that one mechanism — at minimum production-path
determination, generated/derived handling, policy/overlay precedence, and any other control whose governance behaviour
changes with `class`.

> **The architecture property: project-editable classification state cannot silently increase effective authority or
> obtain a governance exemption.**

If changing a class would increase authority, suppress observation, weaken a control, exclude a path from governance or
otherwise confer an exemption, that increase must pass the governed transaction/change-control OC-P2-04 requires.

**The intended capability is preserved.** An authorised governed change may classify paths as evidence/generated/derived.
The owner is explicit: *"The defect is not the capability. The defect is obtaining that capability through an
unauthorised hand edit."*

**Before declaring C complete, search for ALL consumers** of the relevant `class` semantics, not only those AR77-F3
named. The new mechanism must make future consumers depend on one authority source rather than requiring another
synchronised enumeration.

## AR77-F4 and AR77-F5

- **AR77-F4 (hard link).** Independently retest against the new A architecture. **Do not mark it closed merely because
  raw-command trust was removed** — demonstrate its disposition through independent effect-level evidence.
- **AR77-F5 (false runtime message).** Correct the inaccurate explanation around the `curl -k` / argument-indirection
  collision while this surface is being touched. Do not broaden it into unrelated architecture work.

## Evidence classes — builder tests are development evidence only

The owner's ruling, following P2-AR-0077's demonstration that a builder-authored property test quantified only over the
values its own author implemented:

> Builder-authored property tests are NOT automatically independent evidence. … That only proved "the implementation
> behaves correctly over the cases the implementation author imagined." This is insufficient for acceptance.

The A+C implementation worker may and should write regression tests, property tests and negative controls, and should
test its implementation thoroughly — but **all of it remains `BUILDER_DEVELOPMENT_EVIDENCE` and may not close the
architecture findings.** Four classes are kept distinct and must never be collapsed into "tests passed":
`BUILDER_REGRESSION`, `BUILDER_DEVELOPMENT_EVIDENCE`, `INDEPENDENT_ADVERSARIAL`, `HELD_OUT_ACCEPTANCE`.

## The hard stop after the A+C review

If the fresh Opus adversarial review finds another **materially new HIGH** on the install-trust architecture, the
raw-command authority boundary, the authority-enumeration pattern or project-editable exemption semantics — **or leaves a
known HIGH materially open** — the orchestrator **STOPS and returns to the owner**. No further local repair or
enumeration round autonomously. At that point the result is evidence that A+C is insufficient, and the escalation is
toward Option B or another owner-approved architecture review.

## Option B — deferred, recorded, not authorised now

> constrain executable effects through an isolation/sandbox boundary rather than depending on complete semantic
> prediction — **predicted effect is weaker than enforced execution boundary**.

Recorded as a high-priority post-Phase-2 architecture candidate and likely the deeper final architecture. **Not to be
implemented during this remediation** unless A demonstrably cannot satisfy the frozen Phase-2 requirements *and* the
owner explicitly authorises the additional scope.

## Also in force with this decision

- **Worker stall protection** (owner §1) — procedural runtime governance, `ACTIVE` in `ORCHESTRATOR_STATE.yaml`,
  recorded as `IMPLEMENTED_DURING_PHASE_2`. It modifies nothing normative.
- **Performance**: the corrected measurements govern (~50 min full suite; ~2.5 h single-threaded; ~3× penalty; ~40–43 min
  scheduling floor). The ~20–24 min estimate is retracted. No major performance refactor during this remediation.
- **Routing unchanged**; **DeepSeek remains paused** unless the owner explicitly re-enables it.
- **V8.3 stays non-normative** and must not be designed, installed or activated during Phase 2.
- **Record discipline**: every new structured record is schema/parse validated **at write time**.
