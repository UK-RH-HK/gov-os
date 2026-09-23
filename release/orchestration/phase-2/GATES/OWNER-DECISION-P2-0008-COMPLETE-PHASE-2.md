# OWNER-DECISION-P2-0008 — Complete Phase 2 on Option 1; resolve P1; freeze the accepted baseline

| Field | Value |
|---|---|
| Record | Owner decision (product owner, 2026-09-23) |
| Id | **OD-P2-08** |
| Status | IN FORCE. Supersedes the open questions in `PHASE_2_OPTION_B_ESCALATION_PACKAGE.md` and `TRUST_ARCHITECTURE_EXISTING_SOLUTIONS_REVIEW.md` §19. |
| Objective | **Complete Phase 2.** Terminal state: `GOVERNANCE_CAPABILITY_BASELINE_ACCEPTED`, independently earned, followed by a durable `PHASE_2_TO_V8_3_HANDOFF`. |
| Does not change | Contract v3; the frozen Phase-2 acceptance criteria; the accepted R0/R1 Level-1 architecture; D-0007 |

## 1. Architecture accepted — Option 1, and the diagnosis with it

**"Resolve once, execute the object; floor the class."** The owner accepts the research finding that the recurring
defect is a **confused-deputy / ambient-authority** problem: *the check reasons about a representation while the
authority or effect can be determined outside that representation.*

> The architecture must **remove ambient authority** rather than keep extending lists of programs, flags, command
> shapes, class values or consumers.

**No further enumeration-based patch.** Broad architecture exploration does not reopen unless new evidence *falsifies*
the architecture authorised here.

**Level 1 is closed.** SRR/RoT release authenticity, TUF-shaped metadata, signed roles, root rotation,
rollback/high-water, Phase-1 bootstrap and R3 supply-chain assurance are **not to be redesigned**. A Phase-2 finding may
require proving R1 preservation; it must not silently reopen Level 1.

## 2. P1 RESOLVED — the floor is project-specific

**Governance OS governs exactly the repository into which it is adopted.** It imposes **no universal filesystem
layout** and governs no path outside that repository merely because a global template knows of it.

```
gov adopt in Repository X → identify/authenticate X → inventory X's NATIVE structure
  → derive the proposed Project-X floor → consequential adoption decision where required
  → governed owner approval → authenticated Project-X adoption floor → govern X by that floor
```

`src/**`, `backend/**`, `services/**`, `app/**`, `product/**`, `packages/**` are all legitimate. **No universal
`product/**` assumption may be required for brownfield or native repositories.**

The floor's authority comes from **the governed adoption transition and the authenticated machine/kernel chain** — not
from an arbitrary later project edit. After adoption: project-local configuration may add, narrow or strengthen;
ordinary edits **must not silently remove obligations** established by the authenticated floor; changing the
authoritative floor itself goes through the governed route; paths outside the repository stay outside the domain absent
an explicit governed dependency.

**Reuse existing primitives** — adoption, Human Gates, CIT, `cit::binding`, authenticated kernel/project identity,
`human_channel` owner-signed decisions — rather than building a new trust system.

**T2/HMAC sealing is retained as detection and defence in depth, and must NOT be treated as proof-grade owner
authority**, because a process with the owner's OS privileges can read the symmetric key. Proof-grade authority comes
from: *authenticated machine/kernel floor + authenticated project adoption floor + owner-signed governed transition
where widening requires it.*

> **Do not implement "detect whether a human edited this file" as the trust model. Authenticate the authoritative
> transition instead.**

## 3. Property A — resolved execution

> The OS executes a kernel object it holds, never a name it was handed — and **nothing inside that object may silently
> name a second unverified executable object before the first reviewed instruction.**

Use the smallest mature local primitives: resolved absolute object identity; `O_PATH`-held objects; `execveat`-style
execute-the-held-object; a constructed environment; no inherited ambient `PATH`/loader authority; exact digest/review
binding; execution-time re-verification where needed. **Do not recreate shell or interpreter semantics in policy
lists.**

**Shebang closure.** A script reaches the ungated exact-execution path only where the interpreter relationship reduces
to verified executable objects: an absolute interpreter may be resolved, opened and verified inside the *same*
`ResolvedExecution`; a relative interpreter, an `env`-fronted shebang, or `-S`/other re-exec indirection is a
**reduction failure** unless structurally reducible. **Not to be solved by an ever-growing flag list.** Where exact
reduction cannot be proven: `UNDETERMINED` → governed gate or refusal.

**Wrapper chains** (`env`, `nohup`, `timeout`, shell wrappers, interpreter wrappers, opaque chains) **do not
automatically qualify** for the ungated trusted install path. They may still execute — but cannot claim *"the exact
reviewed artefact is necessarily the object that will execute"* unless the complete executable closure is resolved and
verified. Otherwise, the governed route.

## 4. Property C — floor composition, not mutable comparison

**`class` is not an ordered security level, and no bidirectional "more/less privileged" predicate is to be built.** It
is a semantic label whose obligations differ by context.

```
authenticated Project Adoption Floor + applicable immutable kernel floor + project-local additions/narrowing
        ↓
   Effective PathDecision
```

The project-local layer **must not remove obligations from the authenticated floor through an ordinary edit**.
Legitimate change to the authoritative floor runs: proposal → CIT/impact → Human Gate where required → owner-authorised
governed transition → new authenticated floor → evidence invalidation and retest.

Use **type construction and one authoritative resolution point** wherever possible — the research identified
`PathDecision` construction as what makes the property decidable rather than requiring an unfalsifiable search for
every consumer.

**Observability is preserved per OC-P2-04**: the system must report clearly a floored path, a project-added rule, a
governed widening, an **unfloored path where legitimate**, and a refused attempted weakening.

## 5. Reuse, not reinvention

**Do not build a new hand-edit detector.** The research corrected P79-F10: `cit::binding` already provides the
governed-versus-hand-edited pattern, bound to owner-signed Human Decision Gate evidence. The repository contract should
use that existing governed-transition architecture rather than a parallel trust protocol. `"repository-contract"` may
join `SEALED_RECORD_TYPES` as **detection/defence-in-depth**, subject to §2's rule that the seal is not proof-grade.

**`pinned_files` schema gap** is in scope for this implementation: make the authoritative representation explicit, stop
unknown or malformed structure silently acquiring meaning, make runtime interpretation and schema agree, and let
evidence prove semantic equivalence. **Not a broader schema redesign.**

## 6. Deferred — do not implement in Phase 2

**Landlock** → R2 candidate for effect containment. **Full hermetic execution** → later higher-assurance profile.
**bubblewrap / rootless containers / gVisor / microVM** → R3, if the profile ever becomes hostile or multi-tenant.
*Do not introduce Level-3 mechanisms merely because they exist.* The target remains the private, local, owner-controlled
machine.

## 7. Evidence classes and test-author independence

Builder-authored tests are **development and regression evidence only** — and this applies equally to example tests,
negative controls, property tests and generative tests. **A generative test is not independent merely because it
generates many cases.** The fresh reviewer must independently derive the property, the attack domain, the generator
domain, and both negative and positive controls. Classes stay distinct: `BUILDER_REGRESSION`,
`INDEPENDENT_ADVERSARIAL`, `HELD_OUT_ACCEPTANCE` — **never collapsed into "tests passed"**. The implementer must not
see or tune against reviewer-held-out probes before the reviewer's verdict is committed.

## 8. Response to review findings — automatic, with named stops

An ordinary implementation defect **within** this architecture: repair → invalidate affected evidence → fresh review,
**automatically, without returning to the owner**.

**STOP and return to the owner** only if evidence shows: `ResolvedExecution` cannot provide the exact-object property
in this profile; project-specific floor composition cannot satisfy OC-P2-04 or Contract v3; a **new trusted authority**
must be invented; Level 1 / R0 / R1 must be reopened; a Level-3 isolation mechanism becomes **mandatory** for Phase 2;
the product/security/availability/usability boundary materially changes; or another genuine owner-level architecture
decision arises. **No further unbounded enumeration cycle.**

## 9. Anti-stall rule — active for the remainder of Phase 2

The 420-minute coordinator-handshake stall and the ~10-hour self-matching `pgrep -f` wait-loop are now binding lessons.
No unbounded wait loops. Every wait carries a **maximum elapsed time or iteration count, an observable condition, and a
deterministic timeout action**. Prefer tracked PID/process-group state over process-name regex; where pattern matching
is unavoidable, **prove the waiter cannot match itself**. No worker may remain indefinitely `BLOCKED_ON_COORDINATOR`.
States distinguish at least `RUNNING_COMPUTE`, `RUNNING_TOOL`, `BLOCKED_RESOURCE`, `BLOCKED_ON_COORDINATOR`,
`BLOCKED_ON_OWNER`, `STALLED`, `COMPLETE`, with `last_progress_at` freshness. **Rising elapsed time with unchanged
status is a stall signature.** Reconcile the task registry against live process state, output freshness and worker
reports. **Never tell the owner work is "still running" from a stale observation** — obtain current evidence first. A
sleeping waiter is not productive work.

## 10. Minting, verification and completion

**Do not mint `cap2-candidate-2` merely because the builder is green.** Mint only after: P2's disposition is resolved;
the architecture is implemented; builder regression evidence is green; the required full suite is green; a fresh
independent Opus 5 adversarial review finds no blocking defect on the architecture; all relevant HIGHs are
independently closed; and evidence freshness is satisfied. Then freeze the exact tree, compute identity, mint, and
re-establish dependent evidence.

**Formal acceptance verification** is a fresh Opus 5 role — not the builder, the implementation reviewer, or the outer
orchestrator. **The outer orchestrator must not self-award the phase token.** Ordinary defects found there are repaired
automatically, a **new** candidate minted, and a **new** fresh verification run, without relaying routine iterations to
the owner.

**Phase 2 completes only when a fresh independent verifier earns `GOVERNANCE_CAPABILITY_BASELINE_ACCEPTED`.** On
acceptance: a Phase-2 completion package, a reconciled non-normative `V8_3_EVIDENCE_PACKAGE.md`, and a
`PHASE_2_TO_V8_3_HANDOFF.md` sufficient for a fresh Opus 5 session with no chat memory. **Failed iterations are not
erased — they remain historical evidence.**

**V8.3 must not be designed, installed, activated or used to replace V8.2 in this session.** Phase 3 must not be
started here, and must not be started under V8.2 to avoid the V8.3 transition.

## 11. Routing

Outer orchestrator, architecture/security adjudication, adversarial review and formal verification: **Opus 5**.
Cross-cutting implementation: **Sonnet 5**. Genuinely mechanical work: **Haiku**. Build/test/schema: **deterministic
T0**. Per-spawn selection; the outer orchestrator's model is not changed globally. **DeepSeek remains PAUSED.**
