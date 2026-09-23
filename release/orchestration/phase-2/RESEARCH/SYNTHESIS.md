# Trust-architecture prior-art study — synthesis

| Field | Value |
|---|---|
| Run id | **P2-SYN-0001** (architecture synthesiser) |
| Revision | **2** — amended 2026-09-23 after independent challenge by P2-SYN-0002; see §0a |
| Date | 2026-09-23 |
| Nature | **READ-ONLY.** One document written, then amended in place. No product, runtime, kernel, policy, schema or test file touched, in either revision. Nothing implemented. Nothing decided on the owner's behalf. |
| Inputs | `SYNTHESIS-CHALLENGE.md` (P2-SYN-0002, for revision 2); `COMMON-BRIEF.md`; `ORCHESTRATOR-MEASURED-ENVIRONMENT.md`; `AGENT-1`…`AGENT-6`; `PHASE_2_OPTION_B_ESCALATION_PACKAGE.md`; `AGENT_RUNS/P2-AR-0079.run.yaml`; OD-P2-03, OC-P2-04, OD-P2-05, OD-P2-07; `PHASE-2-FROZEN-GATE-CONTRACT.md`; Contract v3; `docs/DECISIONS.md` (D-0007, D-0009, ARCH-0003) |
| Trees read | working tree at `4d42c34` (`release/4.1.6-rc1`) **and** the frozen reviewed tree `35461c9` (`phase2/remediation-ac-review`). Where they differ it is stated; the A+C remediation exists **only** on `35461c9` and is not on the release branch. |
| Evidence added | two probes run on this machine (§1.2, §9.3), both writing only into the session scratchpad. Revision 2 additionally **relies on** two probes produced by P2-SYN-0002 and reproduced by the coordinator (§9.0) — not re-run here, and attributed in the Appendix. |

## 0a. AMENDMENT RECORD — revision 2, 2026-09-23, after independent challenge

This document was challenged by **P2-SYN-0002** (`SYNTHESIS-CHALLENGE.md`), which verdicted it *fit for the owner
after amendment*, and agreed explicitly with its level separation, its dependency declines, the `class`-is-a-label
finding, the Landlock-at-R2 placement, and its refusal to reopen the frozen RoT-1 lineage. **Both corrections to
the owner survived independent verification. The ranking survives.**

**What changed, and why the owner should read the change rather than only the result:**

| # | Amendment | Kind |
|---|---|---|
| **A1** | **§9.2's reduction was defeated by execution.** A `#!` line inside pinned, reviewed bytes executes an unpinned project file *before any reviewed byte runs*. §9.2 now carries a **fourth obligation** that closes it structurally. §9.1's stated property was false as specified and is restated. | **Blocking — architecture changed** |
| **A2** | **§11's minimum is four changes, not three.** The headline sentence is re-counted. | Substantive |
| **A3** | **P79-F8/F9 closure is kernel-layout-only.** For projects onboarded by `gov adopt` with a native layout, floor-composition closes **zero** of that shape. §16 Q3 is restated as a **precondition of the claim**, not a filed question. | **Changes an answer** |
| **A4** | Arithmetic and attribution corrections (§8, §1.3, §1.1, §15): `LOADER_ENV_VARS` is **30** entries not 32; `CLASS_EXEMPTIONS` is 20 lines not 30; comparison total ≈**447** not 457; net ≈**−250** not −260; `migrations/executor.rs:714` is a test; `run_cmd` has **four** call sites not two; the `t2.rs` quote was truncated one sentence early and is completed. | Corrections |
| **A5** | Two findings **strengthened** on the challenger's evidence: the single-chokepoint claim is provable **by type construction**, not by enumeration; and the Property-C floor is **authenticated kernel content**, which I asserted without showing. | Strengthening |
| **A6** | Change 3's size is restated: *one function, one struct field, one retention, one construction site* — not "~40 lines inside an existing function". §15 assumption 3's residual is **not bounded**. | Corrections |
| **A7** | One further probe of the same shape is **recorded as open and not run**: a pinned dynamically-linked ELF artefact with project-controlled `RUNPATH`/`$ORIGIN`/`LD_*`. | Added, unresolved |

**The lesson I am recording against myself, because it is the study's own thesis and this is its fifth instance.**
I found that the escalation package reasoned about a representation (`gov`'s environment) while the effect came
from elsewhere (a program `gov` launched). I then specified a fix that reasoned about a representation (the
descriptor the OS holds) while the effect came from elsewhere (**the first line of the bytes inside it**). The
challenger's probes are the same move applied to me, one level further down. That is not a reason to distrust the
architecture — the remedy is small and in the same idiom — but it *is* a reason to treat "we have now reached the
bottom" as a claim requiring evidence rather than a feeling, and A7 exists because this pattern's track record in
this study is five for five.

I counted `LOADER_ENV_VARS` by its **line count** rather than its **contents** and reported 32 where the answer is
30. In a study whose subject is checks that reason about a representation instead of the thing itself, that is the
error the study is about, committed in miniature, in the document arguing against it. It is corrected in §8 and
flagged here rather than quietly fixed.

## 0. How to read this, and what I did not inherit

The brief told me to re-derive anything my recommendation depends on. I did. Every claim below marked
**[verified]** was checked by me against the named file at the named commit in this session, not taken from a
researcher or from the orchestrator. Two claims are marked **[measured]** — I ran a probe on this machine rather
than reasoning about it, and one of those **falsifies the recommendation the escalation package put to the owner**.

Three things I did *not* do, deliberately: I did not re-run the Phase-2 suite; I did not re-reproduce P79-F8's
end-to-end effect (I verified its mechanism in source instead, which is stronger for an architecture question and
weaker for a severity question); and I did not attempt any integration spike of any candidate technology.

---

# PART I — THE THREE FINDINGS THAT DETERMINE THE ANSWER

## 1.1 P79-F10 is wrong. Property C reduces to extending mechanisms the product already ships. **[verified]**

The escalation package told the owner that Property C faced a prerequisite — *"the product has no mechanism
anywhere to distinguish a governed contract change from a hand edit"* — and that "everything else about C depends
on that answer." I verified the challenger's counter-claim independently at `35461c9` and on the working tree.

**It does not hold. Three separate, shipping mechanisms each already answer it.**

| Mechanism | Evidence I checked myself | What it already does |
|---|---|---|
| `t2::seal_record` / `seal_value` / `verify_record` | `runtime/src/t2.rs` — all `pub`, general-purpose, no CIT coupling | HMAC-SHA256 over canonical content + operation + time, stored in-record as `os_binding`. `Unsealed` and `Broken` are **not honoured**; the typed refusal `T2_UNBOUND` exists and is wired. |
| **`t2::verify_file(root, rel)`** | `runtime/src/t2.rs`, same module | Already generalises the seal **to an arbitrary repository file by relative path**, for `.yaml`/`.yml`/`.md`/`.json`. It is not CIT-shaped and needs no new primitive to point at the path map. |
| **`t2::classify_path`** | same module | Already implements the exact inversion Property C needs, in the product's own words: *"Only paths that carry a seal can be proven OS-written; everything else is the worker's mutation."* |
| `cit::binding` | `runtime/src/cit/binding.rs` | Digest-bound `os_state` block + whole-record seal; *"Consumers never trust the record's top-level fields for an authority decision"*; `binding_sha256` is what a Human Decision Gate carries as `subject.sha256`. |

And the membership fact: `SEALED_RECORD_TYPES = ["human-gate", "cit", "task"]`. The path map is not a member.
**[verified]** So extending this is adding a fourth member to a three-member list and calling an existing public
function, not building a mechanism.

**A schema fact that makes it cheaper than it looks, which no researcher checked. [verified]**
`framework/schemas/repository-contract.schema.json` has **no top-level `additionalProperties`** — so a top-level
`os_binding` seal field is already schema-legal with no schema change at all. Its `paths.items`, however, is
`additionalProperties: false`, so *per-rule* provenance fields would need a schema change. **Whole-file sealing is
free; per-rule sealing is not.** That asymmetry should decide the granularity.

### The trust assumption this carries, which must be stated before anyone relies on it

The T2 seal is **HMAC-SHA256 under a symmetric key held in machine state** (`<state_root>/t2-binding/key.json`,
mode 0600, or a provisioned owner-authority key). The module says so itself, and I am quoting it because the
challenger will look for exactly this and because no researcher surfaced it:

> *"A process running with the **operator's full OS privileges** on a provisioned machine can read the binding key
> (same account) and could compute a seal. Against that attacker the primitive is detection-grade, not proof —
> and, because the requirement is that a record written on one provisioned machine is honoured on the others,
> **what such a process forges on one of the owner's machines is honoured on the others** holding the same key
> (any mechanism meeting the requirement has that property). … The key is symmetric and shared by the machines
> that hold it (`gov` never signs, so no per-machine signature is available): **revocation is per key** (a new
> authority version), **not per machine**."*

**[AMENDED — A4.]** Revision 1 of this document stopped that quote one sentence early, at "detection-grade, not
proof." The omitted sentences make the exposure **worse**: a seal forged on one machine is **honoured on every
other provisioned machine**, and revocation is per key, not per machine — so the blast radius of one compromised
agent is the owner's whole fleet, and the remedy is a new authority version rather than evicting a machine. A
truncation that flatters the recommendation it supports is the one kind this study cannot afford, and the
challenger was right to call it.

The lower-trust party in this deployment profile is *an AI agent running on the owner's machine under the owner's
account*. That is exactly the attacker the module names. **Therefore: sealing the path map, by itself, is
detection-grade against the actual adversary, not proof, and a forgery propagates.** Anyone who tells the owner
that sealing "closes" Property C without those sentences has overclaimed.

Note the second bullet of the same paragraph, which bounds the claim further and which I also did not quote: *"A
process can always run `gov` under a declared role; what it writes that way is an OS operation performed under
that role's authority"* — the agent-identity question is OD-P2-01 and explicitly out of scope. So even a
*correctly* sealed path-map write does not establish *who* asked for it.

Two things rescue it, and they are both already in the product:

1. **The seal is not the authority; the owner signature is.** `runtime/src/human_channel.rs` **[verified]** binds
   a Human Decision Gate answer to an **Ed25519 signature made with a key the machine does not hold** — *"the `gov`
   binary contains no signing code and no key"* — verified against the SRR-provisioned `human-gate` role, with
   use-time re-verification of the stored envelope. `cit::binding` chains to it via `binding_sha256 →
   subject.sha256`. A class change routed through a Human Decision Gate is therefore backed by something an agent
   on this machine **cannot** forge, seal key or no seal key.
2. **Structure beats authentication where it applies.** §1.3 and §10 show that most of Property C does not need
   authentication at all — it needs the kernel floor to stop consulting the project file. A hand edit that is
   *never read for that decision* needs no seal to be inert.

**Conclusion.** Property C reduces to extending existing mechanisms — but the reduction is only sound if it is
stated as *floor-composition (structural, unforgeable) + seal (detection-grade) + owner signature for the one
route that genuinely widens authority (proof)*. That three-part statement is the honest one, and it is what §10
recommends. The orchestrator owes the owner this correction whatever else is decided, as it already noted.

## 1.2 **[MEASURED] The fix recommended to the owner for Property A would not have closed either proven HIGH**

This is the most consequential thing in this synthesis and it is new. The escalation package's §5 and §6 recommend:

> *"Clearing the environment to a controlled allowlist, pinning the working directory so it cannot be overridden,
> and executing the verified artefact by resolved absolute path, would close both."*

The brief told me to prefer measurement over reasoning. I ran the two proven attacks against a **fully cleared
environment** (`env -i`, a fixed `PATH=/usr/bin:/bin`, i.e. strictly stronger than an allowlist) with the working
directory pinned to the project root. Kernel `6.6.87.2-microsoft-standard-WSL2`, GNU coreutils 9.4, unprivileged,
in the session scratchpad.

```
T1  env -i PATH=/usr/bin:/bin  /usr/bin/env PATH=. true
    → MARKER: project ./true RAN (unpinned project file)          ← P79-F1 STILL SUCCEEDS

T2  env -i PATH=/usr/bin:/bin  /usr/bin/env --chdir=decoy sh install.sh
    → MARKER: DECOY install.sh ran (verified bytes != executed)   ← P79-F11 STILL SUCCEEDS

T3  env -i PATH=/usr/bin:/bin  /bin/sh <abs>/install.sh           ← control, wrapper removed
    → MARKER: ROOT install.sh ran (the VERIFIED bytes)            ← the only limb that works
```

**Why.** `env` is not an environment variable — it is *a program Governance OS chooses to execute*. `PATH=.` and
`--chdir=decoy` are **arguments to that program**. `env` reconstructs the environment and changes directory
*inside the child*, after `gov` has irrevocably lost control. `Command::env_clear()` governs what `gov` hands to
`env`; it has no purchase on what `env` does next. `Command::current_dir()` sets the cwd before exec;
`--chdir` overrides it after. The escalation package states this second point itself ("`env --chdir` overrides it
*after the process starts*") and then recommends cwd-pinning anyway.

**So of the three recommended limbs, two are inert and one is load-bearing — and the load-bearing one is the one
stated least precisely.** The property that actually works is not "execute the verified artefact by resolved
absolute path" alongside the wrapper; it is:

> **Do not execute the wrapper chain at all. Execute the resolved artefact, and only it.**

Corollaries the owner should have:

- **Deleting `plain_argument_programs` (the core of Option A) closes neither.** The package already says this of
  F11; T1 shows it is also true of F1 under a cleared environment, because `env` re-supplies `PATH` regardless.
- **The `-C` vs `--chdir=` asymmetry (P79-F13) is not a parsing bug to fix.** Both are `env` doing its documented
  job. Any fix that still runs `env` is fixing the wrong process.
- This is the study's own diagnosis recurring one level up: *the check reasoned about `gov`'s environment; the
  effect came from a program `gov` itself launched.*

## 1.3 The floor/local axis exists — and the *class* consumers are not the problem they were reported to be

The orchestrator verified that `governance/kernel/**` is `owner_role: release-agent, mutation: prohibited` and
`governance/project/**` is `change-controller, restricted`. I re-verified that **[verified]** and add two facts
that change the size of the Property-C fix, neither of which any researcher or the orchestrator established.

**(a) There is exactly one chokepoint, not twelve unknown consumers — and it is provable by construction.
[verified; strengthened per A5]** The review flagged "12 further `.class()` consumers … outside the table," and
OD-P2-07 demanded "search for ALL consumers."

Revision 1 argued this **by enumeration**: I listed every `.class()` call site at `35461c9` and found they all read
`contract().decide(path).class()`. That is true — **22 non-test call sites across 10 modules**, excluding
`policy_precedence.rs:606` (the comparison machinery, which this recommendation deletes):

```
cit/materiality.rs:870          context/receipt.rs:462,671          memory/integrity.rs:310
memory/indexer.rs:210,1548,1667,1672,1700,1705,1827                 memory/manifest.rs:234
orchestration/tasks.rs:954,1882 paths.rs:346,445                    verification/reporting.rs:682
verification/lineage.rs:295,596,981,1077,1082
```

**[CORRECTED — A4]** Revision 1 said "~19 production consumers" and included `migrations/executor.rs:714`. That
line is inside `#[cfg(test)] mod tests`, which begins at line 665 **[verified]** — a test, not a consumer. The
correct figure is 22.

**[STRENGTHENED — A5] But the enumeration is not the argument, and a stronger one is available.** `PathDecision`
is the only type carrying a `.class()` method, and it is **constructed at exactly one place in the entire
runtime** — `paths.rs:710`, the tail of `decide()` **[verified: a grep for `PathDecision {` over every `.rs` file
at `35461c9` returns the struct declaration, the `impl`, `decide`'s return type, that one literal construction,
and `policy_precedence.rs:550`'s signature, which obtains its value *by calling `decide()`*]**.

So "no consumer enumeration is needed" is a **type-level fact, not a search result**. There cannot be an
unenumerated consumer, because there is no other way to obtain the value. This matters beyond tidiness: it is
exactly the move from an **unfalsifiable** proof obligation ("did we find them all?" — the question that defeated
four rounds) to a **single decidable proposition** ("is there a second construction site?"). OD-P2-07 C's "search
for ALL consumers" is discharged **by construction**, which is the strongest form of discharge available and the
one the owner was told could not be reached.

**Property C is therefore a change to one function, and the fix propagates to every consumer by typing.** That is
the "one derived authority source replacing several synchronised enumerations" the brief asks for. Agent 2's
recommendation (§6) converges on it without establishing it; the type-level argument is the challenger's, verified
independently here, and it is better than what revision 1 had.

**(b) The obligation is a positive class match, which no ordering can express. [verified]**
`runtime/src/cit/materiality.rs:870`:

```rust
let class = p.contract().decide(path).class();
if class == "source" {
    m.push("behaviour_change", path, "product source", …);   // → MATERIAL_CHANGE_REQUIRES_CIT
}
```

Meanwhile the "single authoritative predicate" models exemptions through `paths::Exemption`, which has **exactly
two variants** — `TaskMutationObservation` and `ProductionTreeMembership` **[verified]**. `source → test` confers
neither, so `overlap_is_no_less_restrictive` passes it. The predicate is not merely one-directional; it models
**2 of the many distinct authority effects** reachable from `decide().class()`.

This kills the "bidirectional predicate" option (the escalation package's option (i)) on evidence rather than on
principle: you cannot order `source` against `test`. Obligations and exemptions do not share a lattice, and the
project's *own* legitimate classes (`evidence`, `generated`) are neither strictly stronger nor weaker.
**`class` is a label, not a level. Stop trying to order it; own it** (§10).

**(c) The remediation is better than the escalation package implies — and still loses.** I read
`evaluate_path_rules` and `evaluate_path_rules_overlay` at `35461c9` **[verified]**. They do *not* compare by
pattern identity only: `patterns_may_overlap` + `overlap_is_no_less_restrictive` already handle a shadowing
pattern appended under last-match-wins (AR68-F3's lesson, correctly learned). The residual failure is precisely
and only that the comparison's vocabulary is `Exemption`, and the obligation is outside it. That is worth saying
because it shows round 5 was *competent* — which is the strongest possible argument that a sixth round of the
same kind is futile.

## 1.4 The product already concedes the confinement gap — and that changes which problem is open

`runtime/src/tools.rs` **[verified, working tree and `35461c9`]**:

> *"The token and pattern lists in `TOOL_POLICY.installation_envelope` are a **kernel floor, never a safety
> proof**: the OS cannot confine a spawned process, so what it cannot observe is carried by the independent
> governed security review the non-gated branch also requires."*

Read precisely, that sentence scopes the concession to **effects**, not to identity. It says the OS cannot confine
*what a spawned process does*. It does **not** say the OS cannot establish *which bytes it spawns* — and P79-F11
is an identity failure, not an effects failure. Agent 4 is right, and admirably so: **a Landlock ruleset confined
to the project root would not have stopped P79-F11, because `decoy/` is inside the project root.**

So the concession partitions the defect list cleanly, and this partition is the spine of everything below:

| | Identity — *which bytes ran* | Effects — *where the writes landed* |
|---|---|---|
| Defects | P79-F11, P79-F12, P79-F1, AR68/AR73 family | AR77-F1, AR77-F2, AR77-F4 |
| Is it conceded? | **No** — OD-P2-05 clause 1 *promises* it | **Yes** — tools.rs concedes it, and the governed review carries it |
| Right mechanism | resolved-object execution (§9) | kernel confinement (§9.4) |
| Five rounds spent on | trying to *observe* more | trying to *observe* more |

**Answer to the question the brief posed:** yes, the concession changes the right answer — but not in the direction
the measured-environment note suggests. It does *not* make confinement the answer to Phase 2's open HIGHs. It makes
confinement the answer to the *already-disclosed* residual (AR77-F1/F2/F4), and it leaves the two open HIGHs
squarely in the un-conceded identity column, where the fix is cheaper and does not need Landlock at all.

---

# PART II — THE CHALLENGER'S TEST

## 2. Does one mechanism close 2A, 2B and 2C together?

Agent 6's warning is correct and I am upholding it in part: the six-researcher decomposition does mirror the
five-round repair decomposition, and it produced convergent answers partly by shared seed lists (§7.4). Its
proposed unification — a CXI-style "action manifest" binding field authority + exact-effect authorization +
invocation authority to one object — deserves the serious test the brief demands. Here it is.

**The diagnosis unifies. The enforcement does not, and the difference is not cosmetic.**

The unifying diagnosis is right and is 38 years old: Hardy 1988's confused deputy, Miller 2006's *No Designation
Without Authority* / *No Ambient Authority*. Every defect is one party supplying a **designation** that another
party resolves under **different rules**. I adopt that vocabulary (§16, recommendation 1) and weight it far above
the 2026 preprints, per the brief.

But "one diagnosis" does not imply "one mechanism," and the reason is structural, not a matter of ambition:

> **The two deputies are different, and Governance OS controls only one of them.**
>
> - For **2B**, the deputy is the **Linux kernel's `execve`**. Governance OS cannot ask it to re-check anything.
>   The *only* way to make verification and use the same event is to hand the kernel an object it cannot re-resolve
>   — a file descriptor — with an `envp` and `argv` the OS constructed. The fix lives at the **syscall boundary**.
> - For **2A/2C**, the deputy is **Governance OS's own `decide()`**. It controls every read. The fix is to make
>   that function return a floor-composed answer. The fix lives at the **data-model boundary**.
>
> A manifest can *describe* both. It can enforce neither. Bind a manifest to `sh install.sh` and the kernel still
> resolves `install.sh` under `--chdir=decoy` — §1.2 measured exactly that. **A manifest that is consumed as a
> string is one more representation, which is the defect.**

**[STRENGTHENED — A1] This is no longer an argument; it is a measurement.** §9.0's two defeats show the kernel
performing a *second, independent resolution from bytes inside the artefact* **after** the OS has handed it a
descriptor. A CXI-style action manifest binding `{interpreter: sh, artefact: install.sh, argv, envp}` describes
both invocations perfectly and stops **neither**, because nothing consumes the manifest at the instant the kernel
reads `#!`. The defeat happens *below the level at which descriptions exist*. Revision 1 asserted "a manifest can
describe both, it can enforce neither"; that sentence is now backed by two executed attacks, which converts the
adjudication against Agent 6's unification from a contested judgement into an evidenced one.

Agent 6's *framing* contribution stands undiminished and is adopted throughout: Hardy 1988 / Miller 2006 as the
standing vocabulary, and `cit::binding`'s `os_state` block as an already-shipping instance of the manifest shape.
Its warning that the research org chart mirrored the repair org chart is fair and is partly upheld by this
document's own seed-list audit (§7.4). What it does not carry is the conclusion.

**What genuinely does unify, and it is worth having:** one *discipline*, stated once and applied at both sites —

> **Verification emits a resolved object. Use consumes only that object. Nothing between them may re-derive any
> part of it from an input the lower-trust party controls.**

**And here is the finding that makes this more than rhetoric: Governance OS has already implemented the action
manifest, once. [verified]** `cit::binding`'s `os_state` block *is* a CXI action manifest — `content_sha256`,
`impact_sha256`, `binding_sha256`, `writes_sha256`, sealed, recomputed at approve and at execute, bound to an
owner signature. It has been shipping. The correct recommendation is therefore **not** "adopt a mechanism from an
unreviewed 2026 preprint" but **"apply the shape this codebase already proved out, at the two sites that lack
it."** That is a strictly stronger evidential position and it costs the owner nothing in new dependency risk.

**Verdict.** Not three separate fixes; not one mechanism. **One discipline, two enforcement primitives, one
already-proven record shape.** Anything that claims a single mechanism closes 2B has not been measured against
§1.2. I would put that to the challenger as the specific test to apply.

### 2.1 Where I disagree with each researcher, on evidence

| Researcher | Claim | My adjudication |
|---|---|---|
| **Escalation package** | env-clear + cwd-pin + absolute path closes F1 and F11 | **Falsified by measurement (§1.2).** Two of three limbs inert. |
| **Agent 1** | `tough` (WRAP) should replace hand-rolled TUF logic | **Correct in principle, out of scope, and wrongly timed.** It is Level 1. ARCH-0003 is owner-adopted and R0/R1-accepted; the RoT-1 hardening lineage is *frozen pending meta-architecture review*. Proposing to re-implement the accepted Level-1 core during a stopped Phase 2 is exactly the contamination the brief's correction forbids. **Defer to the meta-review, do not action.** |
| **Agent 1** | `fexecve` "closes P79-F11's core directly" | **Overstated as written, correct as amended.** Descriptor-exec closes identity-rebinding *of the object you hold a descriptor to*. It does nothing if you still hold a descriptor to `/usr/bin/env`. Agent 1's own §3.2(a) caveat about interpreter hops is right; the headline is not. |
| **Agent 2** | Git SSH commit signing — **USE DIRECTLY**, "the cheapest possible instance" | **Downgrade to USEFUL LATER.** Three problems Agent 2 flags but does not weigh: (i) it does not cover an uncommitted working-tree edit, which is P79-F8's actual vehicle, so Agent 2 must then bolt on "read from a sealed ref, not the working tree" — a second mechanism; (ii) it makes **git a hard runtime dependency of authority evaluation**, which nothing in the product currently is; (iii) the product already has an owner-signature channel (`human_channel`, Ed25519, key off-machine) that is *strictly stronger* and already wired to gates. Adding SSH signing would be a **second** owner-key custody story. Agent 2's own §10 goal is "one root of trust instead of two" — its recommendation violates it. |
| **Agent 2** | OPA / Rego as WRAP candidate | **Reject for this profile.** Agent 2 itself could not determine whether a Go/WASM evaluator is a realistic embed in a Rust kernel. The transferable idea (AND-composition of independently sourced layers) is ~40 lines of Rust. Taking a policy engine to get an `AND` is the opposite of the brief's §7. |
| **Agent 3** | Bazel `--incompatible_strict_action_env` as the model, ADAPT/REQUIRED NOW | **Right pattern, insufficient alone — and its "REQUIRED NOW" label is falsified by §1.2 unless paired with wrapper elimination.** Agent 3's Q1 answer *does* include "resolve the target to an absolute canonicalised path … execute that same resolved target," which is the correct limb; its own classification table then splits that away from the env work as if either could stand alone. They cannot. |
| **Agent 3** | The Rust `std` fork+exec `environ`-swap is a reason to prefer `Command` | **Correct and well-sourced, and it does not help here.** It makes `Command`'s own `PATH` search honour the child's env. §1.2 shows the child then re-supplies `PATH` itself. Good engineering, wrong layer. |
| **Agent 4** | Landlock is the one REQUIRED-NOW-defensible candidate | **Accept the measurement, decline the priority.** Agent 4's honesty about P79-F11 is exactly right and I am amplifying it. Landlock closes AR77-F1/F2/F4 — which are `MEDIUM` and already disclosed under OD-P2-05 as "effects OD-P2-05 already declares unbounded." It closes **no open HIGH's underlying defect** — precision correction per A4: a blanket "no `LANDLOCK_ACCESS_FS_EXECUTE` under the project root" ruleset *would* stop P79-F1's specific shape, as a containment side-effect that must be carved out the moment any build step legitimately executes a project file; the conclusion is unaffected. Adopting a kernel LSM to close two MEDIUMs while two HIGHs stay open is priority inversion. → **USEFUL LATER / R2** (§13). |
| **Agent 5** | bubblewrap "contingent" on the AppArmor userns restriction | **Inference falsified by the orchestrator's measurement** (this kernel loads no AppArmor). Agent 5's reasoning was sound; record it as corrected, not dropped. Note the correction *raises* bubblewrap's feasibility and does not raise its priority. |
| **Agent 5** | Commit-identity gate (hash the file, compare to a designated commit) — REQUIRED NOW | **Right instinct, wrong primitive.** It has Agent 2's git-dependency problem *and* a fresh one: it accepts **any** commit as governed ("committed ⇒ governed by definition"). An AI agent with repository write access can commit. That converts an authority check into a **no-op against the actual adversary**. `t2::verify_file` + an owner-signed gate is the same idea with a real authority anchor and no new dependency. |
| **Agent 6** | Migrate `policy_precedence` merge to a CUE-style lattice meet — "one of the two or three highest-value findings" | **Reject for `class`, accept for the scalar keys.** §1.3(b): `class` is not orderable, so a meet operator has no meaning for the exact field that failed. Agent 6 reached this from the D027 incident (a *scalar* key) and generalised across a field boundary. For scalar overlay keys the lattice framing is genuinely good; it is not the Property-C fix. |
| **Agent 6** | CXI "action manifest" as the unifying mechanism | **Accept the shape, reject the citation as load-bearing** (§2). The shape is already in `cit::binding`. Per the brief's weighting, a shipping in-repo implementation outranks an unreviewed preprint as evidence. |

---

# PART III — LANDSCAPE, MATRIX, MAPPING

## 3. The landscape per level

**Level 1 — trusting Governance OS itself. Settled; out of scope; do not touch.**
ARCH-0003/SRR-1 is owner-adopted and R0/R1-accepted: TUF-shaped roles, threshold Ed25519 (`verify_strict` only),
two-threshold root succession, durable monotonic high-water marks, verify-then-install with `confirm_unchanged`
and post-swap re-hash. Agent 1's own table showing the retired RoT-1 lineage rediscovering TUF's named attacks one
HIGH at a time is the study's best evidence for the brief's thesis — and is *history*, not a live decision. The
RoT-1 hardening lineage is **frozen by the owner**; `D-0008`/`ARCH-0002` are PROPOSED, not active. **Nothing in
this synthesis depends on, extends, or reopens it.** Agent 1's `tough` WRAP is a real idea for the meta-review's
agenda and must not enter Phase 2.

**Level 2A/2C — governed authority-bearing state.** The mature answer is uniform across five unrelated traditions
(TUF, OPA bundle signing, SELinux compile-then-load, in-toto, object-capabilities): *stop asking whether a change
looks legitimate; make an unauthorised change structurally inert.* The precedence table Agent 2 assembled (§5 of
its report) is the single most useful artefact the study produced, and its punchline survives scrutiny: **every
mature system enforces precedence structurally (who may write / whose signature counts / what the expanded closure
implies); Governance OS is the only entry in the table that enforces it by content comparison.** SELinux's
`neverallow` — a semantic check over the *expanded* policy at compile time, not a syntactic diff — is the closest
prior art, and Governance OS can have its essential property for free because of §1.3(a).

**Level 2B — execution binding.** The prior art is unanimous and cross-traditional: Nix sets
`PATH=/path-not-set` and rewrites shebangs to absolute store paths; Bazel fixes `PATH` to `/bin:/usr/bin` by
default since 0.21 (arrived at for *cache correctness*, independently); Chen/Wagner/Dean 2002 concluded
erase-and-allowlist rather than enumerate-and-blocklist; `fexecve(3)`'s stated rationale is verbatim our use case.
Two things this convergence does **not** give, and both matter: (i) none of them solves the wrapper problem,
because none of them ever *executes an attacker-chosen wrapper* (§1.2); (ii) content-addressing fixes byte
identity, not resolution identity — Agents 1, 3 and 5 each reached this independently and Agent 5 states it best.

**Level 3 — isolation.** Measured, not argued: Landlock ABI 3 works unprivileged on this kernel with real
`EACCES` enforcement; ABI 4 (network) does not exist here; `WRITE_FILE` does not cover file *creation*
(`MAKE_REG` and siblings must be enumerated explicitly). Everything else in the catalogue — gVisor, Firecracker,
rootless containers, WASI, remote execution — is oversized for one owner on one machine, and several have unmet
preconditions here (`kvm` group, `newuidmap`/`newgidmap`). Docker is present as a **root-owned daemon**; building
on it would *regress* the trust boundary.

## 4. Requirement-to-solution matrix

| Requirement (normative source) | What it demands | Mature answer | Classification | Bucket |
|---|---|---|---|---|
| **OD-P2-05 cl.1** — every executed file hash-pinned and re-verified at every execution | verified bytes = executed bytes | `execveat(fd,"",AT_EMPTY_PATH)` — hash the fd, exec the fd | **USE DIRECTLY** (kernel syscall; `nix` crate for the binding) | REQUIRED NOW |
| **OD-P2-05 cl.1** (cont.) — wrapper chains | the wrapper is not the artefact | **execute the resolved artefact; never the wrapper** — Nix/Bazel discipline | **ADAPT** | REQUIRED NOW |
| **OD-P2-05 cl.3** — classification fails closed | unclassifiable ⇒ gate | unchanged; but the *surface* shrinks (§8) | — | REQUIRED NOW |
| **OD-P2-05 cl.5** — pinning is a lifetime property | re-verify at execution | re-open + re-hash + exec the same fd, per invocation | **USE DIRECTLY** | REQUIRED NOW |
| **OD-P2-03 req.2** — envelope computed from trusted OS state | authorised side is not project-editable | floor-composed `decide()` (§10) | **ADAPT** (SELinux `neverallow` / OPA multi-bundle AND) | REQUIRED NOW |
| **OC-P2-04 §1** — narrowing allowed | project may restrict itself | field-wise AND with a per-field order | **ADAPT** | REQUIRED NOW |
| **OC-P2-04 §2** — widening refused, without effect, **and reported** | refusal must be observable | keep `evaluate_path_rules_overlay`'s applied/refused reporting; replace only its comparison | **ADAPT** | REQUIRED NOW |
| **OC-P2-04 §3** — only route to more authority is governed | authenticated/sealed state or approved transaction | `human_channel` owner signature + `t2` seal | **USE DIRECTLY** (in-repo) | REQUIRED NOW |
| **OC-P2-04 §4** — silence is failure | no silent pass | OPA/TUF/SELinux/K8s `failurePolicy` all agree; keep fail-closed | **ADAPT** | REQUIRED NOW |
| **Contract v3 A1** — floors cannot be weakened by lower-precedence policy | structural, not comparative | floor ∧ local | **ADAPT** | REQUIRED NOW |
| **OD-P2-07 A** — no raw/unbound command gets ungated authority | reduce to an exact bound artefact | resolved-object execution | **ADAPT + USE DIRECTLY** | REQUIRED NOW |
| **OD-P2-07 C** — one authoritative source for `class` authority | every consumer derives from one mechanism | **already true** — `decide()` (§1.3a) | **BUILD CUSTOM (≈40 lines, inside an existing fn)** | REQUIRED NOW |
| **AR77-F1/F2/F4** — effects outside the root | confine the process | Landlock (measured ABI 3) | **WRAP** | USEFUL LATER / R2 |
| Descriptor content-race after hashing | immutability across hash→exec | `memfd_create` + `F_SEAL_WRITE` for staged content only | **WRAP** | USEFUL LATER |
| Build provenance | who built it, from what | in-toto Statement shape | **ADAPT** | R2 |
| Public multi-party non-repudiation | transparency log | Sigstore keyless | **NOT APPLICABLE** | R3 |
| Hostile co-tenancy | strong isolation | gVisor / Firecracker / microVM | **WRAP** | R3 |

## 5. Defect-by-defect: would the recommendation actually have prevented it?

Held to Agent 4's standard. **R = the recommended architecture (§9 Problem A + §10 Problem C, Option 1).**

| Defect | Sev | Would R have prevented it? | Why — precisely |
|---|---|---|---|
| **P79-F11** `env --chdir=decoy sh install.sh` | HIGH | **YES** | R never executes `env`. The classifier reduces the command to a resolved artefact set; `env` is not an artefact, so the command is `undetermined` and gates, or the operator declares `sh` + `install.sh` and R execs `/bin/sh`'s fd with `<abs>/install.sh` as an argument constructed by the OS. Measured T3 confirms the resolved form runs the verified bytes. **Residual: none for this shape.** |
| **P79-F12** same shape at `health_check.command` | HIGH | **YES** | Same call site; OD-P2-05 cl.5 re-verification is the same code path. |
| **P79-F1** `env PATH=. true` | HIGH | **YES — but not for the reason the package gave** | Not because the environment is cleared (measured T1: that fails), but because `env` is not executed and `true` is not a pinned artefact, so the command never reaches the ungated path. **Residual: if a project legitimately pins `/usr/bin/env` as an artefact, R must still refuse to pass through *its* argv — see §15, assumption 3.** |
| **AR68/AR73 family** (~40 shapes) | — | **YES, as a class** | Wrapper chains, flag bundles, attached-value inline code, flagless interpreters, and slash-spelling divergence all stop being able to change what the kernel executes. They can still change what a *log* reads, which is a reporting concern, not an authority one. |
| **P79-F8** `{pattern: product/*.py, class: test}` | HIGH | **YES for kernel-layout projects. NO for `gov adopt` native layouts** | `cit::materiality:870` reads `decide(path).class()`. Under floor-composition, `product/app.py` is matched by the kernel rule `product/**`, so its class comes from the kernel rules only and the obligation is never lost. **But `adopt.rs:1579/1585` generates unfloored `{d}/**` rules for any non-`product/` layout, so for those projects the same edit against `src/*.py` still works (§10.4).** Closure is conditional on extending the floor to declared project roots — **precondition P1**, not a filed question. |
| **P79-F9** same edit escapes lineage W7 | HIGH-adj | **YES, same condition** | `lineage.rs:981` filters on `CODE_CLASSES.contains(decide(rel).class())` — same chokepoint, same fix, **same layout qualification**. |
| **Direct-artefact `#!` re-resolution** (`["install.sh"]` with `#!./w` or `#!/usr/bin/env -S PATH=. sh`) | — | **NO for revision 1's §9; YES with obligation 2** | Measured defeat of revision 1's specification (§9.0). The remedy is §9.2 obligation 2 + §11 change 4. Listed here because it was *created* by the recommendation and must not be invisible in its own scorecard. |
| **AR77-F3** second consumer of `class` | closed | **YES, and structurally** | The class a consumer sees is floor-owned wherever a kernel rule matches, so a *future* unknown consumer inherits the property without being enumerated. This is the specific thing OD-P2-07 C asked for. |
| **P79-F10** "no mechanism exists" | MEDIUM | **N/A — the finding is false** (§1.1) | Three mechanisms exist. R uses two of them. |
| **AR77-F1** empty-authority `file://` | MEDIUM | **NO** | The write is performed by the *spawned process*, correctly executing verified bytes. R establishes identity, not effects. Closed only by §9.4 (Landlock) or by the governed review, which OD-P2-05 cl.4 already assigns. **State this plainly; do not let R be sold as closing it.** |
| **AR77-F2** absolute path inside a token | MEDIUM | **NO** | Same. |
| **AR77-F4** hard link | MEDIUM | **NO** | Same, and worse: `openat2`'s `RESOLVE_BENEATH`/`RESOLVE_NO_SYMLINKS` explicitly do not cover hard links — there is nothing to canonicalise. Only an inode/device boundary check or kernel confinement reaches it. |
| **P79-F3b** decoupled scan can remove a finding | LOW | **NO** | Untouched. It is a reporting-accuracy defect, correctly graded, and should stay on the register. |
| **R0/R1 unauthenticated-source attacks** | — | **NO, and R must not claim to** | Level 1. Answered to the accepted extent by SRR-1's verify-then-install transaction and monotonic high-water marks; the residual is the *frozen* RoT-1 question. R touches nothing here. §14. |

**Score, restated without spin [AMENDED — A3]: R closes 4 of 4 open HIGHs (P79-F1, F8, F9, F11) plus F12 and the
AR68/AR73 class — with P79-F8 and P79-F9 closed for kernel-layout projects and conditional on precondition P1
(§10.4) for `gov adopt` native layouts. It closes 0 of the 3 open MEDIUMs (AR77-F1/F2/F4) and 0 Level-1
findings.** The execution half (F1, F11, F12, AR68/AR73) carries no layout condition.

That is the honest boundary, and it matches the partition in §1.4 exactly — which is a consistency check, not a
coincidence. **The one thing the boundary must not be allowed to hide** is that revision 1's own fix *created* a
new instance of the identity column (the `#!` row above) and had to be amended to close it; a scorecard that
counts only inherited defects flatters whatever produced it.

## 6. USE DIRECTLY / WRAP / ADAPT / BUILD CUSTOM

Consolidated across all six researchers, adjudicated, with the brief's burden of proof on `BUILD CUSTOM`.

| Candidate | Class | Bucket | Note |
|---|---|---|---|
| `execveat(2)` / `fexecve(3)` | **USE DIRECTLY** | NOW | Measured working here for binaries *and* `#!` scripts (§9.3) |
| `O_PATH` + `O_NOFOLLOW` descriptor acquisition | **USE DIRECTLY** | NOW | correct way to obtain the fd |
| `nix` crate (`unistd::{execve,execveat,fexecve}`) | **WRAP** | NOW | MIT, actively released; `std` has no descriptor-exec at all |
| `std::process::Command` `env_clear`/`current_dir` | **USE DIRECTLY** | NOW | necessary hygiene; **not sufficient** (§1.2) |
| Bazel fixed-`PATH` + `--action_env` allowlist | **ADAPT** | NOW | hangs off the existing `tool.schema.json` declaration surface |
| Chen/Wagner/Dean erase-and-allowlist | **ADAPT** | NOW | supersedes the 30-entry `LOADER_ENV_VARS` denylist (§8) |
| `t2::seal_value` / `verify_file` / `classify_path` | **USE DIRECTLY (in-repo)** | NOW | detection-grade; see §1.1 caveat |
| `human_channel` owner signature (Ed25519, key off-machine) | **USE DIRECTLY (in-repo)** | NOW | the only *proof*-grade authority anchor available |
| `cit::binding` `os_state` manifest shape | **ADAPT (in-repo)** | NOW | the already-proven action manifest (§2) |
| SELinux `neverallow` — semantic check over expanded state | **ADAPT** | NOW | the pattern behind floor-composition |
| OPA multi-bundle AND-composition | **ADAPT** | NOW | the operator, not the engine |
| Object-capability discipline (Hardy '88, Miller '06) | **ADAPT (vocabulary + audit method)** | NOW | free; prevents re-enumeration |
| Saltzer & Schroeder complete mediation | **ADAPT** | NOW | the oldest correct statement of the defect |
| Floor-composed `decide()` | **BUILD CUSTOM** | NOW | **Justified**: one function, one struct field, one retention, one construction site (§10.3), reusing the existing kernel-template baseline and the existing `owner_role`/`mutation` axis. No external primitive expresses "this project's path map" |
| Landlock (`landlock` crate) | **WRAP** | **LATER / R2** | measured ABI 3; closes AR77-F1/F2/F4; closes no HIGH |
| `memfd_create` + `F_SEAL_WRITE` | **WRAP** | LATER | only for content the OS stages itself |
| seccomp-bpf | **WRAP** | LATER | answers "which syscall", not "which path" |
| bubblewrap | **WRAP** | LATER | right shape for a whole subprocess tree; new binary + bespoke flag policy |
| git signed commits + `allowed_signers` | **USE DIRECTLY** | **LATER** — downgraded | second key-custody story; misses uncommitted edits (§2.1) |
| `tough` (TUF client) | **WRAP** | **DEFERRED to the frozen RoT meta-review** | Level 1; not Phase 2 |
| in-toto Statement shape | **ADAPT** | R2 | fills a field ARCH-0003 already reserves |
| CUE lattice-meet | **ADAPT (scalar keys only)** | LATER | wrong tool for `class` (§1.3b) |
| Nix / Guix store | **ADAPT (pattern only)** | LATER | ecosystem cost ≫ the two ideas worth having |
| OCI content addressing | **ADAPT (confirmation only)** | — | independently confirms artefact ≠ invocation |
| Flux / Argo CD, Gatekeeper / Kyverno | **ADAPT (pattern only)** | R3 | cluster-shaped; reconciliation needs the daemon this profile excludes |
| gVisor, Firecracker, rootless containers, WASI, remote execution | **WRAP** | R3 | hostile-multi-tenant tools for a non-multi-tenant profile |
| Sigstore keyless, TPM sealing, Uptane, `AT_EXECVE_CHECK` | **NOT APPLICABLE** | — | online CA / no guest TPM / no fleet / needs kernel ≥6.14 (this is 6.6.87) |

**Only one `BUILD CUSTOM` survives**, and it is ~40 lines of logic inside a function that already exists, plus three small touch points (§10.3). That is the
result the brief's §7 asked for.

## 7. Where the researchers converged — and whether it was convergence or a shared seed list

The brief asked me to test this specifically. Three convergences, graded:

- **"Never let ambient `PATH`/env/cwd decide what executes."** Nix (purity), Bazel (cache correctness), Chen et
  al. (setuid safety), Rust std maintainers (rust-lang/rust#157144, in flight). **Genuine.** Four traditions, three
  different motivations, no shared seed list, and one of them is not a security motivation at all. This is the
  strongest single result in the study.
- **"Authority must be established at write time, not inferred at read time."** TUF, OPA, SELinux, in-toto,
  git, Perkeep, Dhall, object-capabilities. **Genuine but over-attributed.** Agents 1, 2, 5 and 6 all reached it,
  and all four seed lists contained TUF and signing. The claim survives because §1.1 shows the codebase reached it
  independently, for CIT records, before this study existed. That in-repo instance is worth more than the eight
  citations.
- **"Sandbox it."** Agents 4 and 5 both landed on namespace/LSM confinement. **Seed-list artefact, and both agents
  said so.** Agent 4 explicitly argued *against* its own REQUIRED-NOW case and demonstrated it would not have
  stopped P79-F11; Agent 5 reached bubblewrap from Bazel, i.e. from a build-reproducibility premise, not from the
  defect list. Two agents given isolation-shaped scopes recommending isolation is not evidence. **I am treating
  this convergence as non-load-bearing** and ranking it accordingly (§13, §17 Option 2).

**A fourth convergence nobody noticed, and it is the alarming one.** Every researcher, and the escalation package,
and the orchestrator, described P79-F1 as an *environment* defect. It is not — it is a *wrapper-execution* defect
that merely uses an environment variable as its payload (§1.2). Six agents inherited that framing from the brief's
own §2 table, which says "the exec inherits the environment, so `PATH` rebinds the program **after**
classification." That sentence is true and it is the wrong causal level, and it propagated unchallenged into the
recommendation put to the owner. **This is the clearest live instance of the study's own thesis: everyone reasoned
about a representation of the defect, and the effect came from somewhere the representation did not cover.**

---

# PART IV — RECOMMENDED ARCHITECTURES

## 8. What gets deleted — quantified

Measured at `35461c9` unless stated.

**Execution (Problem A).** `TOOL_POLICY.installation_envelope` holds **106 enumerated entries** total. Of those,
**45 exist solely to predict what a command will execute** and are deleted by resolved-object execution:

| list | entries |
|---|---|
| `opaque_recipe_programs` | 14 |
| `inline_code_flags` | 9 |
| `wrapper_programs` | 8 |
| `script_interpreters` | 6 |
| `flagless_code_programs` | 4 |
| `argument_indirection_flags` | 2 |
| `plain_argument_programs` | 2 |
| **subtotal deleted** | **45** |

The remaining **61** (`host_authority_tokens` 28, `credential_patterns` 9, `privilege_tokens` 9,
`host_authority_classes` 4, `host_scope_flags` 4, `policy_paths` 4, `network_classes` 2, `credential_classes` 1)
answer a *different* question — would this installation expand authority — and **are not deleted**. They remain a
kernel floor for the review trigger. I am stating this because it would be easy, and wrong, to claim "106 entries
deleted."

Also deleted: **`LOADER_ENV_VARS`, 30 entries** (`runtime/src/capabilities/binding.rs`), replaced by
`env_clear()` + a fixed `PATH` + a declared allowlist. Worth noting why this list is itself evidence: it is the
product's *best* existing environment defence and **it is a denylist that does not contain `PATH`, `IFS` or
`GIT_SSH_COMMAND`** **[verified — full list re-derived by parsing its string literals]**. The mechanism BC-P2-40
built to stop code substitution omits the variable that P79-F1 uses. Erase-and-allowlist is not a refinement of
this; it is its replacement.

> **[CORRECTED — A4] Revision 1 said 32.** I had counted the declaration's *lines* rather than its *entries*. The
> list holds 30 strings. In a document arguing that checks must reason about the thing rather than its
> representation, counting a list by its representation is the error the document is about, committed in
> miniature. It is recorded rather than quietly fixed because the study's own standard requires it — and because
> it is a reminder that the 45/61 split above was checked entry by entry and this was not.

Plus: `skip_wrappers` and its `is_flag`/`is_env_assignment`/`is_bare_number` token heuristics
(`tools.rs:981-1000`), and the `-C` vs `--chdir=` asymmetry (P79-F13) that no list can fix.

**Authority state (Problem C).** Line counts of the comparison machinery at `35461c9` **[verified by measurement
of the function spans]**:

| function / item | lines |
|---|---|
| `evaluate_path_rules_overlay` | 131 |
| `path_rule_narrowing` | 90 |
| `overlap_is_no_less_restrictive` | 83 |
| `evaluate_path_rules` | 71 |
| `CLASS_EXEMPTIONS` table | **20** *(corrected — A4; 22 with its doc comment)* |
| `rule_effective_attrs` | 16 |
| `describe_exemptions` | 13 |
| `Exemption` enum | 10 |
| `class_exemptions` | 7 |
| `class_confers`, `patterns_may_overlap` | 6 |
| **total** | **≈447** *(corrected from 457)* |

Floor-composition replaces the **comparison** — roughly 300 of those lines — with a second `decide()` pass over
the kernel rules and a field-wise AND. The **reporting** (~130 lines of applied/refused records that OC-P2-04 §2
and §4 require, feeding `gov policy overrides` and doctor D027) is **retained**, not deleted. Net ≈ **−250 lines
of hand-written security comparison logic** *(corrected from −260)*, and the `Exemption` vocabulary disappears
entirely. Every other span above was independently re-measured and matches exactly.

**What replaces it is not free either [A6]:** one function, one struct field, one retention, one construction site
(§10.3). The net is still strongly negative, but "~40 lines" was the code and not the change.

**Reductions in the brief's own terms:**

| Metric | Before | After |
|---|---|---|
| Authority sources for `class` | project file, with the kernel template consulted *comparatively* | one: the kernel rules decide any path they match |
| Enumerations that must be kept complete | 45 exec-semantics entries + 32 loader vars + 2 exemptions + 14 class values × 19 effects | **0** for execution semantics; **0** for class authority |
| Custom security comparison code | ≈447 lines | ≈130 (reporting only) |
| Consumers that must be found and updated | feared 12+; **actually 1** — and `PathDecision` has exactly one construction site, so there *cannot* be another (§1.3a) | 1, correct by **typing**, not by search |
| Proof surface | "did we enumerate every shape / every consumer?" (unbounded, **unfalsifiable**) | three bounded, testable propositions: "does `decide()` return the floor where a kernel rule matches?", "is the exec'd fd the hashed fd?", **"is every program the kernel resolves before the first reviewed instruction in the hashed closure?"** (the third added by A1) |
| TCB | + the classifier's semantic model of every shell/interpreter on earth | + two syscalls already in the kernel |

**The most important deletion is not a line count.** It is that both remaining propositions are **falsifiable by a
single test each**, whereas "have we enumerated everything?" has been unfalsifiable for five rounds — which is
precisely why five rounds each ended with a reviewer finding one more.

## 9. Recommended architecture — Problem A (execution trust)

### 9.0 **[AMENDED — A1] The defeat that changed this section, and why it is not a disclosure**

Revision 1 of §9 stated its guarantee as *"the interpreter that runs is the one intended, on the bytes reviewed."*
**That was false as specified.** The independent challenger implemented §9.2 exactly — `open(O_PATH|O_NOFOLLOW)`,
OS-constructed `envp`, OS-pinned cwd, `execveat(fd,"",argv,envp,AT_EMPTY_PATH)` — and made a hash-pinned, reviewed
artefact execute an **unpinned, unreviewed project file**, twice, by two routes. The coordinator reproduced both
independently. I take them as established and have not re-run them.

| attack — artefact's **first line** is the whole payload | observed |
|---|---|
| `#!./w` (relative interpreter) | `UNPINNED-W-RAN` |
| **control:** same artefact, cwd *not* pinned to the project root | fails `ENOENT` |
| `#!/usr/bin/env -S PATH=. sh` | `UNPINNED-LOCAL-SH-RAN` |

**Read the control row.** The first attack does not merely survive the cwd pin — it **requires** it. §9.2(1)'s
mitigation supplies the attacker's resolution root. The second defeats §9.2(3) ("construct the environment") with
four bytes inside the reviewed artefact: the shebang names `/usr/bin/env` *absolutely*, so nothing the OS does to
`PATH` matters, and `-S` rebuilds the environment inside the child. **That is P79-F1 reconstructed inside a
conforming, pinned, byte-verified installation under a fully constructed environment.**

**Neither is an instance of §9.4's disclosed limit.** Both act *before a single reviewed byte executes*, and both
decide *which* interpreter runs. They violate **OD-P2-05 clause 1** directly, and they violate §9.1's own stated
property: the OS held the object; **the object handed the kernel a name.** Therefore the remedy below is
**structural — a fourth obligation the reduction must enforce — not a limitation to disclose.** Disclosure is not
available where a normative clause is breached.

**The cause is this study's own thesis, one level further down than I looked.** `execveat` hands the kernel a
verified object; the kernel then performs a **second resolution from bytes inside that object**. I applied that
pattern to the escalation package's recommendation and did not apply it to my own. It is recorded in §0a against
myself, and it is the reason §16 Q8 exists.

**Two consequences worth stating before the remedy:**

1. **This strengthens the rejection of Agent 6's one-mechanism answer (§2), converting a contested judgement into
   an evidenced one.** A CXI-style action manifest binding `{interpreter, artefact, argv, envp}` **describes both
   invocations perfectly and stops neither**, because nothing consumes the manifest at the instant the kernel
   reads `#!`. *"A manifest can describe both. It can enforce neither"* was an argument in revision 1; it is now a
   measurement.
2. **It does not favour Option 2 or Option 3.** `./w` is a *declared input* — it would be bind-mounted into a
   bubblewrap jail and permitted by a Landlock ruleset scoped to the project root. Both attacks survive inside
   Option 3 unchanged. The ranking is unaffected.

### 9.1 The property **[restated]**

> **The OS executes a kernel object it holds, never a name it was handed — and nothing inside that object may name
> a second one.** Verification produces a `ResolvedExecution` whose closure includes *every* program the kernel
> will resolve on the way to the first reviewed instruction; execution consumes only that; nothing in between
> re-derives any part of it.

The clause after the dash is the amendment. Revision 1's property stopped at the descriptor, which is precisely
where the kernel starts resolving again.

### 9.2 The shape, in **five** obligations

1. **Reduce, do not classify.** For each declared command, the OS attempts to reduce it to a
   `ResolvedExecution { interpreter: Option<Fd>, artefact: Fd, argv: Vec<OsString>, envp: Vec<OsString>, cwd:
   AbsPath }` where every `Fd` was obtained by the OS from an absolute canonical path and hashed **through that
   descriptor**. **If the reduction fails for any reason, the command is `undetermined` and gates** — OD-P2-05
   clause 3 unchanged. A wrapper program is a reduction failure, not a token to skip. *This is the limb §1.2
   proves is load-bearing.*
2. **[NEW — A1] Resolve the artefact's own first line, or refuse.** The reduction reads the artefact's first
   line and **fails (→ `undetermined` → gate)** unless *either* the artefact has no `#!`, *or* the `#!` names an
   **absolute** interpreter path which the OS itself resolves, opens and hashes **inside the same
   `ResolvedExecution`**, and which is **not itself a re-exec vector**. A relative `#!` path, an `env`-fronted
   `#!`, a `#!` carrying `-S`, or a `#!` naming a program that is not in the resolved closure is a **reduction
   failure**, not a shape to normalise.

   **The starting point already exists in-repo, and reusing it unchanged would reproduce the defect.**
   `runtime/src/memory/profile.rs:378` implements `fn shebang(file) -> Option<String>` **[verified]**, and that
   module's own header states the interpreter so found is *"content-hashed"* (`profile.rs:19`) — so the product
   already knows, **in one subsystem**, that a shebang decides which executable runs and must be hashed. The
   installation classifier never reads one. *This is §1.1's move recurring at the execution boundary: the
   primitive exists and was never pointed at this surface.* But its `env` special case is
   `parts.find(|a| !a.starts_with('-'))` **[verified]**, which for `#!/usr/bin/env -S PATH=. sh` skips `-S` and
   returns **`"PATH=."`** as the interpreter. **Reuse it; do not reuse it unchanged.**

3. **Execute the object.** `execveat(artefact_fd, "", argv, envp, AT_EMPTY_PATH)`, with the interpreter's own
   descriptor when the artefact is a script and the descriptor **not** opened `O_CLOEXEC` (§9.3).
4. **Construct the environment; do not filter it.** `env_clear()`, then a fixed OS-owned
   `PATH=/usr/bin:/bin` (Bazel's shipped default since 0.21), a disposable OS-owned `HOME`, and an explicit
   per-tool allowlist. The natural home is the existing `tool.schema.json` declaration surface, which already
   carries `permissions`, `required_permission_classes`, `capabilities`, `credential_scope`, `version_pin` and
   `installation_sha256` — this answers Agent 3's one open obstacle. **Note obligation 2 is what makes this
   obligation hold**: without it, `#!/usr/bin/env -S …` discards everything constructed here in one exec hop.
5. **Re-verify at every execution.** Re-open, re-hash, re-exec per invocation — OD-P2-05 clause 5, unchanged in
   requirement, now cheap because hash and exec share one descriptor. **The closure re-verified must include the
   interpreter resolved under obligation 2**, not only the artefact.

**[AMENDED — A4] Scope correction.** Revision 1 scoped this property to *"`util::run_cmd`'s two install call
sites."* `run_cmd` has **four** call sites at `35461c9` **[verified]**: `tools.rs:2151` and `tools.rs:2566` (the
install path, the two the open HIGHs live on), plus **`adopt.rs:622`** (a detected native test command) and
**`verification/product.rs:255`** (`pl.command`, a project-declared verification plan). The latter two execute
**project-influenced** command vectors through the same program-by-string, no-`env_clear` path. Neither is an open
HIGH, so this qualifies *scope*, not correctness — but the honest statement is **"two call sites for the minimum,
four for the property,"** and a property applied to half its call sites is the shape this study exists to stop.

### 9.3 Feasibility — measured on this machine, not cited

Compiled and ran an unprivileged C probe against kernel `6.6.87.2-microsoft-standard-WSL2`:

| Case | Result |
|---|---|
| `execveat(fd,"",AT_EMPTY_PATH)` on a **binary** (`/bin/true`) | **SUCCESS** |
| `execveat(fd,"",AT_EMPTY_PATH)` on a **`#!` script** | **SUCCESS** |
| Same, with the descriptor opened `O_CLOEXEC` | **REFUSED, `ENOENT`** |
| `/dev/fd`, `/proc/self/fd` | both present |

The third row is the trap Agent 3 flagged from the man page; it is now confirmed empirically here. **The safer-
looking flag silently breaks the mechanism on exactly the conforming `sh install.sh` case that P79-F11 is about**,
and it fails with a misleading `ENOENT`. It belongs in the acceptance tests as a named negative control — it is
the same *shape* of defect as Agent 4's Landlock `MAKE_REG` trap and as the five rounds themselves: the mechanism's
advertised property is not the property needed.

### 9.4 What Problem A does not close, stated before anyone claims otherwise

**[AMENDED — A1] What is no longer on this list.** The `#!` re-resolution was *never* on it and could not have
been: it breaches OD-P2-05 clause 1, which is normative, so it must be **enforced** (obligation 2) rather than
disclosed. The boundary between "enforced" and "disclosed" is exactly this: *does a reviewed byte execute first?*
If the defect acts before the first reviewed instruction, it is a binding failure and belongs in §9.2. If it acts
after, it is the interpreter's own behaviour and belongs here.

- **The direct-artefact install shape needs the same rule.** The classifier admits not only
  `["sh", "install.sh"]` (the shape every certification fixture uses) but also `["install.sh"]` directly, via
  `looks_like_a_file` → `classify_file_candidate`. For that shape there is no declared interpreter at all, so
  obligation 2 is the *only* thing standing between a pin and an unpinned `#!` target. Either apply the shebang
  rule to it or refuse the shape (require a declared interpreter). **This is §11's change 4.** Not verified
  end-to-end by anyone: the challenger derived its admissibility from source and did not run
  `gov tools install --execute` against it. As an architecture requirement it stands regardless; as an
  *exploitable finding* it needs that run, which is cheap (§16 Q8).
- **AR77-F1/F2/F4.** Effects of a correctly-executing verified process. Kernel confinement (§17 Option 2) or the
  governed review (OD-P2-05 clause 4, already the design).
- **A malicious-but-correctly-pinned artefact.** OD-P2-05 says so explicitly; that is the division of labour.
- **What the interpreter does next.** Every bare name inside `install.sh` is a fresh unpinned resolution. Closing
  that needs a full declared closure (Nix-scale) — out of proportion, and honestly out of scope. **Level 2B's
  guarantee stops at "the intended interpreter ran the reviewed bytes."** Say so in the owner-facing text; do not
  let it be read as more.
- **Content mutation between hash and exec on a file that stays on disk.** Narrowed to one descriptor's lifetime,
  not eliminated. `memfd_create` + `F_SEAL_WRITE` closes it only for content the OS stages itself.

## 10. Recommended architecture — Problem C (governed authority-bearing state)

### 10.1 The property

> **Where a kernel rule matches a path, the kernel rules decide it. The project file is consulted only where the
> floor is silent, and only to narrow.**

Note what this deletes: it is not "compare the project file to the kernel template and refuse widenings." It is
"**do not ask the project file that question at all.**" That is the SELinux `neverallow` move — a semantic check
over the expanded effective state — and it is Agent 2's "floor AND local, never floor compared against local."

### 10.2 The shape, in four obligations

1. **Two decisions, composed.** `RepositoryContract::decide` computes a **floor decision** over the kernel
   template's rules alone and a **local decision** over the full list. It returns:
   - **`class`, and every authority-bearing attribute, from the floor** wherever a kernel rule matched the path;
   - **field-wise AND** (per-field restrictive order: indexing `false < true`; `mutation` `prohibited` strictest;
     `agent_read`, `export`, `sensitivity` as already ordered) for everything else;
   - the local decision alone where no kernel rule matched.
   **`class` is not AND-composed, because it is not ordered (§1.3b) — it is floor-owned.** This is the single
   design decision the whole of Problem C turns on.
2. **One chokepoint, therefore no consumer enumeration.** All 22 non-test consumers read `decide().class()`, and
   — the stronger form — `PathDecision` has **exactly one construction site** in the runtime **[verified §1.3a]**.
   OD-P2-07 C's "search for ALL consumers" is discharged **by type construction**, not by a search, which is the
   thing four previous rounds could not achieve.
3. **Seal the file; refuse to honour an unsealed or broken one — as an integrity check, not as the authority.**
   Add `"repository-contract"` to `SEALED_RECORD_TYPES`, seal on every governed write, and call the **existing**
   `t2::verify_file`. Top-level `os_binding` is already schema-legal (§1.1). This catches accidental and
   unprivileged edits and makes them *reported*, satisfying OC-P2-04 §4. It is **detection-grade against a
   same-account agent** and must be described that way.
4. **Route genuine widening through the owner signature.** Where a project must change a kernel-matched path's
   class (a legitimate capability OD-P2-07 explicitly preserves), it goes through a Human Decision Gate whose
   answer is Ed25519-signed with a key `gov` does not hold, exactly as `cit::binding` already does via
   `binding_sha256 → subject.sha256`. **This is the only limb that is proof-grade rather than detection-grade**,
   and it is the correct answer to OC-P2-04 §3.

### 10.3 Does this build on the existing axis or replace it?

**It builds on it, and that is why it is small.** The kernel template already declares `owner_role:
release-agent, mutation: prohibited` for `governance/kernel/**` and `change-controller, restricted` for
`governance/project/**` **[verified]**, and `evaluate_path_rules` already resolves the kernel template as the
floor baseline. Floor-composition changes *what is done with* that baseline — from comparison to composition —
and touches no schema, no policy file and no template. Nothing is replaced.

**[STRENGTHENED — A5] The floor is authenticated kernel content, and this is the best fact in the Property-C
story.** Revision 1 asserted that floor-composition "needs no key"; it did not show why that is safe. Verified
now: `PolicySet::load` takes `kernel_dir = trust.policy_root` from `kernel_trust::trust(root)`
(`policy.rs:117`) **[verified]**, and that function's own contract is explicit —

> *"Constitutional content is read only from a kernel that has been **authenticated against the installed release
> identity** (`kernel_trust`); when verification fails the immutable payload **embedded in this binary is
> substituted explicitly** and the substitution is recorded (verifier V-H2)."* — `policy.rs:112-114`

So the floor is not a project-editable file and not a file at all in the untrusted sense: it is release-identity-
authenticated kernel content, with an explicit, recorded fail-safe to the binary's embedded payload. **That is why
floor-composition is stronger than the seal rather than merely cheaper** — the seal is detection-grade under a
symmetric key an agent can read (§1.1), whereas the floor rests on the accepted Level-1 chain (ARCH-0003) without
introducing any new dependency on it. It is the one limb of Property C that is structurally sound against the
actual adversary, and it should be the limb the owner is told about first.

**[CORRECTED — A6] And the size of the change, restated honestly.** Revision 1 called this "~40 lines inside an
existing function," and §17's reversibility row called it "one function plus one string in a three-member const."
Both understate it. Verified: `Project::contract()` builds `RepositoryContract::new(overlay().get(…))`
(`project.rs:176`); `RepositoryContract` carries `data`, `roots`, `rules`, `sensitivity` — **no kernel template**
(`paths.rs:555-560`); and `repository_contract_baseline` is a **local variable** inside `PolicySet::load`
(`policy.rs:410`), not retained **[all verified]**. Floor-composition therefore needs **one function, one struct
field, one retention, and one construction site** — still small, still the right shape, but four touch points, not
one.

**One rail already exists and reduces the work.** `contract()` reads the **effective** overlay, not the raw file:
`Overlay::get` returns `set_effective`'s value when present, and `contract()` calls `policies()` (which sets it)
first **[verified]**. So the precedence layer's refusals already reach every `decide()`; floor-composition rides
that rail rather than laying it.

### 10.4 **[AMENDED — A3] The limit of this fix. It is a hole, not a footnote, and it changes an answer.**

**The floor's coverage equals the kernel template's coverage.** The template covers `governance/**`, `spec/**`,
`product/**`, `archive/**`, `**/.env*`, `**/secrets/**`, `.governance-runtime/**`, `.governance-state/**`.

Revision 1 stated that accurately and then filed the consequence as an open question. **That placement was wrong,
and the challenger is right that it is load-bearing.** Verified myself at `35461c9`, `adopt.rs:1579` and `:1585`:

```rust
for d in &test_dirs { extra.push(json!({"pattern": format!("{d}/**"), "class": "test",   …})); }
for d in &src_dirs  { extra.push(json!({"pattern": format!("{d}/**"), "class": "source", …})); }
```

with `d` excluded only when it is one of `spec|governance|archive|product|docs`. So for any repository whose
source or tests are not under `product/`, `gov adopt` generates `src/**`, `app/**`, `lib/**`, `cmd/**` as
**project-declared patterns with no kernel counterpart — hence no floor.**

**The consequence, stated plainly, because it changes a "YES" into a qualified one:**

> For a project onboarded by `gov adopt` with any layout other than the kernel's own, **floor-composition closes
> zero of P79-F8 and P79-F9's shape.** `{pattern: "src/*.py", class: test}` still cancels
> `MATERIAL_CHANGE_REQUIRES_CIT` at `cit/materiality.rs:870`, and still drops the file out of
> `lineage.rs:981`'s `CODE_CLASSES` filter. The *instance* is closed because **this** repository uses `product/`.
> The *capability* is untouched for the population `gov adopt` exists to serve.

This is structurally the same finding as the RoT-1 review's "64 of 125 leaves unfloored," recurring here — which
is itself a reason to take it seriously rather than as an edge case.

**What follows for the recommendation.** Not rejection — floor-composition is still right, and it is the only limb
that is structurally sound (§10.3). But three things change:

1. **§5's verdict and §17's Option 1 row must read "closes P79-F8/F9 for kernel-layout projects."** Amended.
2. **"Is the floor extended to declared project roots?" is a precondition of the closure claim, not a question to
   file.** Amended in §16 as **P1**, ahead of the numbered questions.
3. **"This path is unfloored" must be observable** in `gov policy overrides` and doctor — otherwise the gap is
   silent, which OC-P2-04 §4 ("silence is failure") independently forbids.

Anything that presents floor-composition as total is overclaiming. Revision 1 came close to doing so in two
sentences, and they are corrected.

## 11. **[AMENDED — A2]** The smallest thing that closes the two open HIGHs — and how it differs from the architecture

The brief asked for this separation explicitly, and it matters because the owner may want the minimum.

**The minimum, for both open HIGH classes — four changes, not three:**

| # | Change | Closes | Size |
|---|---|---|---|
| 1 | In the installation classifier, treat a **wrapper program as a reduction failure** (`undetermined` ⇒ gate) instead of a prefix to skip. Delete `skip_wrappers` and `wrapper_programs`. **No replacement detector is needed** — the classifier's existing inverted default already gates an unrecognised program. | **P79-F11, P79-F12, P79-F1** | one function deleted, one branch changed |
| 2 | Exec the **resolved absolute artefact** (and resolved absolute interpreter), with `env_clear()` + fixed `PATH`, at `util::run_cmd`'s two **install** call sites (of four — §9.2). | hardens 1; closes the residual `PATH` shapes | ~20 lines |
| **4** | **[NEW]** **Resolve the artefact's own `#!` line into the hashed closure, or refuse** (§9.2 obligation 2); and for the direct-artefact shape `["install.sh"]`, either apply that rule or require a declared interpreter. | the two measured defeats of §9 (§9.0) — **without it, changes 1–2 still let a pinned artefact run an unpinned file** | one first-line read + one resolution; `memory/profile.rs::shebang` is the starting point, amended for `-S` |
| 3 | In `RepositoryContract::decide`, take **`class` from the kernel rules** wherever a kernel rule matches. | **P79-F8, P79-F9** (kernel layouts; see P1), and AR77-F3 structurally | one function, one struct field, one retention, one construction site |

**That is it. Four changes, no new dependency, no new crate, no kernel feature, no schema change.** Measured
T1/T2/T3 say change 1 is the one that actually matters for A; §9.0's probes say change 4 is not optional; and
§1.3(a) says change 3 needs no consumer sweep.

> **Why change 4 is in the *minimum* and not in the architecture.** Changes 1–2 close the two *inherited* HIGHs.
> But they leave — and change 2 partly *enables*, via its own cwd pin — a route by which a reviewed artefact runs
> an unpinned file before any reviewed byte executes, breaching OD-P2-05 clause 1. Shipping 1–2 without 4 would
> close two proven attacks and open one measured one. **Any sequencing that defers change 4 past changes 1–2
> should be refused.**

**What the minimum is *not*:**

- It is **not** descriptor-based execution. Change 2 closes the *identity-rebinding* attacks that exist today;
  `execveat` closes the *TOCTOU window* between hash and exec, which is a narrower, un-demonstrated residual. Add
  it when implementing the architecture, not to close the HIGHs.
- It is **not** the T2 seal on the path map. Floor-composition alone makes P79-F8 inert **where the floor
  reaches** (§10.4). The seal adds observability (OC-P2-04 §4) and is the only thing that speaks at all to the
  unfloored paths `gov adopt` generates — which raises, rather than lowers, its importance for the adopted-project
  population, while remaining detection-grade (§1.1).
- It is **not** the owner-signed route for legitimate class changes. That restores a *capability*; it does not
  close a defect.
- It is **not** Landlock. Landlock closes no HIGH (§5).

**The relationship.** The minimum is the first increment of the architecture and is strictly contained in it —
every line survives into the full form. It is not a patch to be unwound later. But the minimum leaves two
properties unestablished that the architecture provides and that a verifier will ask about: hash-to-exec atomicity
(needs `execveat`) and "unsealed authority state is refused and reported" (needs the seal). **A verifier could
reasonably accept the minimum on the HIGHs and still record both as residual.**

## 12. The local/private, R2 and R3 split

**REQUIRED NOW (private/local integrity — closes the open Phase-2 HIGHs):** wrapper-as-reduction-failure;
resolved-artefact execution with a constructed environment; floor-composed `decide()`; the T2 seal on the path map
with its honest detection-grade framing; fail-closed and *reported* on every refusal (OC-P2-04 §4); adopting
confused-deputy / ambient-authority vocabulary as the standing audit method.

**USEFUL LATER (R2 release certification):** `execveat`-based descriptor execution and `memfd_create` sealing for
staged content; **Landlock** as the effects backstop that closes AR77-F1/F2/F4 (with the `MAKE_*` rights
enumerated explicitly and ABI-3 degradation handled); schema-constraining `pinned_files` and adding
`additionalProperties: false` to `tool.schema.json`; in-toto Statement shape for the evidence-digest field
ARCH-0003 already reserves; a bubblewrap-style declared-input sandbox if the AR68/AR73 *effects* surface needs to
be closed rather than reviewed; git signed commits **if and only if** the owner wants a second custody story.

**HIGH-ASSURANCE ONLY (R3 / hostile / multi-tenant):** gVisor, Firecracker/microVMs, rootless containers, WASI
component model, remote execution, Sigstore keyless + transparency log, TPM sealing (not reachable from this WSL2
guest), full Uptane, seL4/Capsicum re-platforming, `AT_EXECVE_CHECK` (needs kernel ≥6.14; this is 6.6.87).

**DEFERRED TO THE FROZEN META-REVIEW (Level 1, not Phase 2):** Agent 1's `tough` WRAP; any change to SRR-1's
role model, rotation, threshold or high-water logic.

## 13. New dependencies and their risks

| Dependency | Where | Risk | Mitigation | Verdict |
|---|---|---|---|---|
| **None** | the §11 minimum | — | — | **The minimum adds zero dependencies.** That is its strongest property. |
| `nix` crate (MIT, v0.31.x) | `execveat`/`fexecve` | small, active, widely used; `std` has no descriptor-exec | pin + `installation_sha256`; ~1 function used | **Accept at R2** |
| `landlock` crate (MIT/Apache-2.0) | effects backstop | maintained by the kernel feature's own author; TCB delta ≈ 0 (kernel already trusted) | `Compatible` API degrades on ABI change; **must enumerate `MAKE_*`, `REMOVE_*`, `REFER`** | **Accept at R2 if AR77-F1/F2/F4 are to be closed** |
| **Kernel capability (not a package): `execveat`** | — | present since 3.19; **measured working here**. WSL2 kernels update; a future kernel could regress | design must degrade to change 2's absolute-path exec, not fail open | **Accept, with a stated degradation path** |
| bubblewrap (external binary) | declared-input sandbox | new binary to fetch/verify/pin; **its own docs say the security is entirely the flag list you write** — a bespoke policy is the whole boundary | — | **Decline for now.** Replaces one bespoke enumeration with another |
| OPA/Rego, CUE toolchain | policy | new runtime/toolchain for an operator expressible in ~40 lines | — | **Decline** |
| git as a *runtime authority dependency* | Property C | promotes an optional tool to a trust component; misses uncommitted edits | — | **Decline for now** (§2.1) |
| `tough` | Level 1 | would re-open a frozen lineage | — | **Decline / defer** |

**Two non-obvious risks that belong in front of the owner:**

1. **The T2 symmetric-key assumption (§1.1).** Any Property-C story resting on the seal rests on a key an
   AI agent on this machine can read. The mitigation is architectural, not cryptographic: floor-composition needs
   no key at all, and the owner signature uses a key that is not on the machine. **Do not let the seal carry
   weight it cannot bear.**
2. **`pinned_files` is not in `tool.schema.json`, and that schema has no top-level `additionalProperties`
   [verified at `35461c9`].** The field carrying the entire OD-P2-05 "bind the bytes" guarantee is described by
   nothing: not its presence, not its shape, not its types, and unknown fields are permitted. Every Property-A
   option leans on descriptor-declared data — including the environment allowlist in §9.2(3). **Any
   descriptor-declared security data must be schema-constrained, or the check reasons about an unvalidated
   representation, which is this study's defect verbatim.** This is a new observation, not in scope to fix here,
   and it should travel to whoever implements §9.

## 14. Level separation — does anything here import a Level-3 concern?

Audited deliberately, because the brief says this failure mode is easy to commit and the challenger will look for
it.

| Item | Level | Verdict |
|---|---|---|
| Wrapper-as-reduction-failure | 2B | clean |
| Resolved-artefact execution, constructed `envp`/cwd | 2B | clean |
| `execveat` descriptor execution | 2B | clean — a plain syscall, not an isolation boundary. **Not** Level 3 despite superficially "syscall-level" framing |
| Floor-composed `decide()` | 2A/2C | clean |
| T2 seal on the path map | 2A | clean — reuses an in-repo primitive |
| Owner-signed route for class widening | 2A | clean — reuses `human_channel`, already wired to gates |
| **Landlock** | **3, used as a 2B compensating control** | **Contaminating if placed in REQUIRED NOW.** It is a kernel LSM security boundary. Agent 4 argued both sides honestly and declined to make the call; I am making it: **R2, not now.** It closes no open HIGH's underlying defect (§5), and pulling a Level-3 mechanism into a stopped Phase 2 to close two already-disclosed MEDIUMs is precisely "solving an R3 problem inside Phase 2 because the technology exists." |
| bubblewrap / containers / gVisor / Firecracker / WASI | 3 | excluded |
| `tough` / TUF re-implementation | **1** | **excluded — and this is the direction contamination would most likely come from.** The RoT-1 lineage is frozen; importing it would re-open a loop the owner closed |
| Sigstore keyless, TPM | 3 | excluded (and TPM unavailable) |

**One honest admission.** §9's `ResolvedExecution` record borrows its *shape* from the capability literature
(Hardy, Miller) and from CXI, which are Level-3-adjacent intellectual traditions. Borrowing a **shape** is not
importing a **mechanism**: nothing in §9 adds a kernel boundary, a sandbox, a namespace or a privilege. If a
challenger argues otherwise, the test is concrete — name the Level-3 *component* §9 or §10 introduces. There is
none.

## 15. Unstated trust assumptions, stated

1. **The kernel is trusted.** Already in the profile. `execveat` and any future Landlock work both rest on it.
2. **The T2 binding key is readable by any process running as the owner's account — including the AI agents that
   are the lower-trust party.** The module says so; §1.1 restates it. **The seal is detection-grade against the
   actual adversary.** Every Property-C claim must be phrased accordingly.
3. **`argv` handed to a pinned artefact is still attacker-influenced. [AMENDED — A6: the residual is NOT
   bounded.]** §9 binds *which bytes run*. It does not bind what the artefact is told to do. Revision 1 predicted
   in prose that "a project that pins `/usr/bin/env` as its artefact reconstructs P79-F1 inside a conforming
   install," and proposed refusing to admit programs whose job is to re-execute another — calling that residual
   *"smaller and bounded."*

   **The challenger executed that prediction and corrected the adjective.** A byte-identical **copy** of
   `/usr/bin/env` at an arbitrary project path (`cp /usr/bin/env proj/tools/setup`) satisfies the pin exactly,
   never leaves the project root, and with `["tools/setup", "PATH=.", "true"]` runs a project-local `./true`.
   **No name-based list reaches a copy.** Only a content denylist would, and that is unbounded.

   **The honest placement, therefore, is not "a small enumeration" but the concession §9.4 already makes.** This
   residual is **co-extensive with "what the interpreter does next"** and belongs to **OD-P2-05 clause 4's
   governed review**, which the architecture already relies on and which the owner already accepted as the
   division of labour. Presenting it as a bounded list would be inventing a sixth enumeration in the document
   arguing against enumerations.

8. **[NEW — A1] The artefact's own first line does not choose the interpreter.** This assumption was nowhere
   stated in revision 1 because it was not noticed, and the challenger's probes broke it. It is listed here for
   completeness, but **listing it is not the remedy**: OD-P2-05 clause 1 is normative, so the architecture must
   **enforce** it (§9.2 obligation 2), not disclose it. An assumption that a normative clause depends on is a
   requirement wearing the wrong label.
4. **The kernel template is trusted and complete for the paths it covers.** Floor-composition inherits the
   template's coverage exactly; §10.4 is the consequence.
5. **The owner's private signing key is off this machine** (`human_channel`'s stated premise, ARCH-0003 §1). If
   that ceases to be true, the only proof-grade limb degrades to detection-grade.
6. **Bus factor of one.** Single-owner single-key custody is a deployment-profile limit, not a defect, and caps
   any "authenticated" claim below a two-party SLSA Source-track level. Say it rather than imply more.
7. **One machine, one moment.** Landlock ABI 3, `execveat`, and the absent AppArmor restriction are all
   measurements of this WSL2 kernel today. WSL2 kernels update. Anything depending on them must degrade safely
   (fail closed toward the gate), never assume persistence.

## 16. Open questions needing an owner decision

### **P1 — a precondition, not a question [A3]**

**The floor must be extended to declared project roots, or the P79-F8/F9 closure claim must be narrowed to
kernel-layout projects.** This is not something to file alongside the questions below, because a claim in §5 and
§17 depends on its answer. `gov adopt` generates unfloored `{d}/**` source/test rules for every non-`product/`
layout (§10.4, verified at `adopt.rs:1579/1585`), so for the population `gov adopt` exists to serve,
floor-composition closes none of that shape. Either the kernel template gains a mechanism for flooring
project-declared roots (for example: a declared root inherits the floor of the kernel role it claims), or the
owner accepts a closure scoped to this repository's layout — **and the scoping is stated wherever the closure is
claimed.** Both are defensible; silence is not.

### **P2 — one probe, recorded as open and deliberately not run [A7]**

**A pinned, dynamically-linked ELF artefact with a project-controlled `RUNPATH`/`$ORIGIN`, or `LD_*` reaching
`run_cmd`.** This is the same shape as the two defeats in §9.0 — a second resolution performed from data inside or
beside the verified object — at the layer below the shebang: the dynamic loader. It matters because
**`LOADER_ENV_VARS` is stripped on the *plugin* path only (`apply_plugin_env`), not at `run_cmd`** **[verified]**,
so the install path has no loader-variable hygiene at all today.

I have **not run it and I do not assume its outcome.** What I will say is that this pattern's record in this study
is five for five — the escalation package's fix, revision 1's fix, and three of the five repair rounds all failed
at exactly one level below where they looked — and that a design which reaches implementation without this probe
would be repeating the one mistake this study has documented most thoroughly. **It is a pre-implementation
obligation, not an owner decision**, and it is cheap.

### The owner decisions

1. **Is the corrected Property-A recommendation authorised?** §1.2 falsifies what the escalation package proposed.
   The owner has not yet been asked to authorise "do not execute wrapper chains" — which is a *behaviour change*
   for projects whose installers legitimately use `env`, `nohup` or `timeout`. **This is the one question that
   must be answered before any work starts.**
2. **Is detection-grade acceptable for the path-map seal?** Given §1.1's key exposure, does the owner accept
   detection-grade integrity for authority-bearing config, with proof-grade reserved for the owner-signed gate
   route? (This is the question Agent 2 correctly declined to answer.)
3. **~~Should the floor extend beyond the kernel template's path coverage?~~ → promoted to precondition P1
   above.** It is not an optional extension; a closure claim depends on it.
4. **What is the legitimate governed route for a class change, and what does it cost in workflow?** OD-P2-07
   preserves the capability. Routing it through a Human Decision Gate makes every path-map edit an owner-signed
   event. Acceptable, or too heavy?
5. **Landlock at R2, or never?** It closes AR77-F1/F2/F4. It is a Level-3 mechanism. The owner has said
   Option B is "likely the deeper final architecture" — is Landlock the increment, or is bubblewrap-style
   declared-input sandboxing?
6. **Re-scope (the escalation package's Option C)?** Orthogonal to all of the above and still live. **The two
   corrections change its arithmetic in opposite directions:** Property C is much smaller than reported (P79-F10
   is false; one chokepoint, not twelve consumers), which argues for finishing it; Property A's recommended fix
   was wrong, which argues that the surface is harder to reason about than anyone has yet demonstrated. My read,
   offered as input and not as a recommendation: the §11 minimum is small enough that re-scoping to avoid it buys
   little, but that is the owner's judgement, not mine.
7. **`pinned_files` schema gap** (§13). Fix now, or record as R2? It is not exploited; it is the same defect class
   as AR73-F4 one field over.
8. **[NEW — A1] Should the direct-artefact install shape (`["install.sh"]`) be supported at all, or refused in
   favour of a declared interpreter?** §9.4. Refusing it is strictly simpler and removes the shape the two
   measured defeats used; supporting it means §9.2 obligation 2 must carry the whole weight for it. **Related and
   cheap:** nobody has run `gov tools install --execute` end-to-end against that shape — the challenger derived
   its admissibility from source. That run is what would grade §9.0's defeats as an *exploitable finding* rather
   than an *architecture defect*. They stand as an architecture defect either way, because they defeat the
   prescription regardless of which shapes reach it.

---

# PART V — THE OPTIONS

Three coherent architectures, ranked. Not a catalogue: each is a complete position, and each strictly contains the
one above it.

## OPTION 1 — **Resolve once, execute the object; floor the class** *(recommended)*

| | |
|---|---|
| **Existing technology / pattern used** | `execveat(2)`/`O_PATH` (kernel, **measured working here** for binaries and `#!` scripts); `std::process::Command` `env_clear`; Bazel's fixed-`PATH` + `--action_env` allowlist (shipped default since 0.21); Chen/Wagner/Dean 2002 erase-and-allowlist; SELinux `neverallow` semantic-closure check; OPA multi-bundle AND-composition; **in-repo**: `t2::seal_value`/`verify_file`/`classify_path`, `human_channel` Ed25519 owner signature, and `cit::binding`'s already-proven action-manifest shape. |
| **What Governance OS still has to build** | A `ResolvedExecution` reduction (wrapper ⇒ `undetermined`) at the two `util::run_cmd` **install** sites — of four for the full property (§9.2); **shebang resolution into the hashed closure (§9.2 obligation 2)**, starting from `memory/profile.rs::shebang`, amended for `-S`; descriptor acquisition + hash-through-fd + `execveat`; a constructed `envp` hanging off `tool.schema.json`; floor-composition — **one function, one struct field, one retention, one construction site**; `"repository-contract"` added to `SEALED_RECORD_TYPES`; an owner-gated route for legitimate class widening. **One `BUILD CUSTOM`.** |
| **Assurance achieved** | Closes **all 4 open HIGHs** (P79-F1, F8, F9, F11) + F12 + the AR68/AR73 class — **P79-F8/F9 for kernel-layout projects, conditional on precondition P1 for `gov adopt` native layouts (§10.4)**. Property A's guarantee is falsifiable by **two** tests ("is the exec'd fd the hashed fd?" and "is every program the kernel resolves before the first reviewed instruction in the hashed closure?") rather than by an unbounded enumeration. Property C's guarantee is *structural*, discharging OD-P2-07 C's "find all consumers" **by type construction**. **Does not close AR77-F1/F2/F4** (effects) or anything at Level 1. |
| **Complexity** | Low. Two call sites for A's minimum (four for the property), one function plus three touch points for C. No new crate for the §11 minimum; one small crate (`nix`) for the descriptor-exec increment. |
| **Likely effort** | §11 minimum: small — **four** changes, no dependency. Full Option 1 with descriptor-exec, the seal and the owner-gated route: moderate, dominated by test/negative-control authoring (the `O_CLOEXEC` control, **and a `#!` control per §9.0's two shapes**) and by the workflow design for Q4, not by the code. Add probe P2 before implementation. |
| **Effect on the TCB** | **Net reduction.** Removes the classifier's semantic model of shells and interpreters (45 policy entries + `skip_wrappers`), the **30**-entry loader denylist, and ≈250 lines of comparison logic. Adds two syscalls in a kernel already trusted, plus one first-line read. The `landlock`/bubblewrap/container TCB is *not* added. |
| **Effect on Phase-2 acceptance** | Directly addresses both OD-P2-07 limbs at the level the owner asked ("remove the pattern, not another enumeration"). Positive for **AC-3** (the remaining PARTIALs get *argued* rather than *enumerated* justifications) and **AC-4**. Neutral to **AC-14** — it changes `product_code_digest`, so R1 re-verification is required either way. Leaves AR77-F1/F2/F4 as disclosed residual, which is where OD-P2-05 clause 4 already placed them. |
| **R2 path** | Add Landlock for the effects residual; add `memfd_create` sealing for staged content; schema-constrain `pinned_files`; in-toto Statement shape for evidence digests. Each is additive. |
| **R3 path** | Unchanged and unblocked: bubblewrap → rootless containers → gVisor/microVM, in that order, if the profile ever becomes multi-tenant. Option 1 does not foreclose any of it. |
| **Reversibility** | **High, and this is its second-strongest property — with one qualification neither I nor the challenger verified.** A is two call sites and a policy-list deletion; C is one function, one struct field, one retention, one construction site; the seal is additive (a top-level field the schema already permits); the owner-signed route is a removable gate. **No data migration, no format change, no external dependency to unwind, no schema change.** **The qualification:** deleting `wrapper_programs` from `framework/policies/TOOL_POLICY.yaml` changes the kernel payload, hence `KERNEL_MANIFEST.json`, `framework.lock.kernel_manifest_hash`, the binary's embedded payload and this machine's SRR installation record — so "revert the code" is not the same as "revert the release transaction," and `ENFORCEMENT_MAP.yaml` coverage (`policy_coverage.rs` treats "declared but does nothing" as a finding) is a second small edit. **Neither of us attempted it.** "Reversible in an afternoon" is right about the code and is an unverified claim about the release transaction. |

**The case against, stated fairly:** it does not close AR77-F1/F2/F4, so a reviewer who regards those as the real
remaining risk will find Option 1 incomplete. It leaves §15 assumption 3 as a residual that is **not bounded** — a
byte-identical copy of an exec vector satisfies any pin — properly assigned to OD-P2-05 clause 4's governed review
rather than to a list. And **its own specification was defeated once already** (§9.0); the remedy is small and in
the same idiom, but the honest inference is that the *next* level down (probe P2, §16) deserves checking before
implementation rather than after.

## OPTION 2 — Option 1 **+ kernel confinement at the spawn site**

| | |
|---|---|
| **Existing technology** | Everything in Option 1, plus **Landlock** via the `landlock` crate — measured ABI 3, unprivileged, real `EACCES` enforcement, no daemon, no root, TCB delta ≈ 0 (the kernel is already trusted). |
| **What to build** | A ruleset attached in a `pre_exec` closure at `capabilities/host.rs::invoke()` (which already uses the Unix extension trait for `process_group(0)`) and at the install sites, granting exactly the declared paths. **The work is the rights enumeration, not the plumbing.** |
| **Assurance** | Option 1's, **plus AR77-F1/F2/F4 closed structurally** — an empty-authority `file://`, a token-embedded absolute path and a hard link all resolve to a real inode through a real syscall, and Landlock mediates the syscall, not the string. It collapses a whole class of present *and future* path-obfuscation spellings into one kernel decision. |
| **Complexity** | Moderate. One crate; ABI-3 degradation; and one real trap: **`WRITE_FILE` does not cover file creation** — `MAKE_REG`/`MAKE_DIR`/`MAKE_SYM`/`MAKE_FIFO`/`REMOVE_*`/`REFER` must all be in `handled_access_fs` or creation is unrestricted **everywhere, silently**. Also: ABI 3 has **no network rights** on this kernel, so network confinement is unavailable here. |
| **Likely effort** | Option 1 plus a bounded increment, most of it in getting the rights set right and testing it. |
| **Effect on the TCB** | Smallest possible for a confinement mechanism: no daemon, no new binary, no privilege, one small crate by the kernel feature's own maintainer. |
| **Effect on Phase-2 acceptance** | Would move AR77-F1/F2/F4 from disclosed-residual to closed. **But it introduces a Level-3 mechanism into Phase 2 (§14)**, and closes zero open HIGHs. |
| **R2/R3 path** | This *is* the R2 increment; R3 would replace it with bubblewrap or a container runtime if a whole subprocess tree ever needs confining. |
| **Reversibility** | High but lower than Option 1: a new crate in the dependency graph, and the rights enumeration becomes a maintained artefact that must track ABI changes. Removing it re-opens AR77-F1/F2/F4. |

**The case against:** it is a Level-3 mechanism closing MEDIUMs while HIGHs are open (priority inversion); its
rights set is a new enumeration that must be kept complete — the very shape the brief says has failed five times,
relocated one layer down; and Agent 4, whose scope it is, explicitly declined to assert it should be built.
**Recommended as R2, not now.**

## OPTION 3 — Hermetic declared-input execution (the full Option B)

| | |
|---|---|
| **Existing technology** | bubblewrap (or direct namespace syscalls) composing mount/user/PID/net namespaces — Bazel's `linux-sandbox` mechanism, Flatpak's engine. Unprivileged user namespaces **measured working on this machine** (and Agent 5's AppArmor objection **measured not to apply here**). |
| **What to build** | A per-invocation jail exposing only declared, verified paths, with a cleared environment and no network unless declared — **plus a declared path allowlist for every governed operation**. |
| **Assurance** | Highest of the three for *effects*: undeclared filesystem access fails structurally; AR77-F1/F2/F4 and the whole AR68/AR73 effects surface collapse into one boundary. **Still does not close P79-F11** on its own — `decoy/` is a declared input — so **Option 1's reduction remains necessary inside it.** That is the decisive point: Option 3 is a *superset* of Option 1's need, not a substitute for it. |
| **Complexity** | High. A new external binary to fetch, verify and pin; a flag policy that, per bubblewrap's own documentation, *is* the entire security boundary; and a per-operation input declaration for every governed tool. Bazel's own history shows `--incompatible_strict_action_env` took years to make default because rules implicitly depended on ambient `PATH`. |
| **Likely effort** | Substantially larger than Options 1–2, and front-loaded onto authoring and maintaining declarations rather than onto code. |
| **Effect on the TCB** | Net addition: one external binary plus a bespoke, security-critical flag policy owned entirely by Governance OS. |
| **Effect on Phase-2 acceptance** | Out of proportion to a stopped Phase 2. OD-P2-07 records Option B as "not to be implemented during this remediation" absent explicit owner authorisation. |
| **R2/R3 path** | This *is* the R3 path, reached early. |
| **Reversibility** | **Lowest.** Path declarations become a product-wide authoring surface projects depend on; removing the sandbox later means removing a contract with every governed tool. |

**The case for it anyway:** it is the only option that makes "what a verified artefact does next" a bounded
question, and OD-P2-07 already names it as the likely deeper final architecture. **The case against now:** it
replaces one enumeration (command shapes) with another (path declarations), the brief's §7 test is
"fewer enumerations," and it does not close either open HIGH without Option 1 inside it.

---

## Ranking, and the single sentence

**1 › 2 › 3, unchanged after independent challenge.** Option 1 closes every open HIGH, deletes more than it adds,
needs no new dependency for its minimum, and is reversible at the code level. Option 2 is its correct R2
successor. Option 3 is a genuine architecture whose time is not now and which — decisively — **needs Option 1
inside it regardless**: `./w` is a declared input, so §9.0's two defeats survive inside a bubblewrap jail
unchanged.

**[AMENDED — A2] The single sentence, re-counted.** Revision 1 said "the same three changes." It is four, and the
owner will quote whichever number is printed:

> **The recommended Property-A fix would not have worked — measured, on this machine — and the Property-C
> prerequisite the owner was told to settle first does not exist; both problems reduce to the same four changes,
> none of which needs a new dependency.**

Two qualifications the owner should carry with that sentence, neither of which changes it:

- **The fourth change exists because this document's own first fix was defeated the same way** (§9.0). That is
  evidence the *method* works — specify, attack, amend — and evidence that "we have reached the bottom" is a claim
  needing a probe, not a feeling. Probe **P2** (§16) is the next one and has not been run.
- **P79-F8/F9's closure is scoped to kernel-layout projects** until precondition **P1** (§10.4) is settled. For
  repositories `gov adopt` onboards with a native layout, that shape remains open.

---

## Appendix — evidence I produced in this session

**Probe 1, §1.2** (`scratchpad/p2syn-probe.sh`): P79-F1 and P79-F11 attempted under `env -i
PATH=/usr/bin:/bin` with cwd pinned to the project root. Both succeeded; the wrapper-free control ran the verified
bytes. GNU coreutils 9.4, kernel 6.6.87.2-microsoft-standard-WSL2.

**Probe 2, §9.3** (`scratchpad/fdexec.c`): `execveat(fd,"",AT_EMPTY_PATH)` on a binary → success; on a `#!`
script → success; with `O_CLOEXEC` → `ENOENT`; `/dev/fd` and `/proc/self/fd` present.

**Evidence I did NOT produce, and am relying on (revision 2).** §9.0's two defeats, and §15 assumption 3's
pinned-copy attack, were produced by **P2-SYN-0002** (`SYNTHESIS-CHALLENGE.md`, probes 1–2) and **independently
reproduced by the coordinator**. I have not re-run them and I am not claiming them as mine. They are taken as
established on two independent reproductions; the amendments they drive (§9.0, §9.2 obligation 2, §11 change 4,
§15 assumption 3 and 8) are mine.

**Source claims re-derived by me for revision 2** (not inherited from the challenge): `LOADER_ENV_VARS` parsed to
its 30 string literals, confirming no `PATH`/`IFS`/`GIT_SSH_COMMAND`; `CLASS_EXEMPTIONS` span = 20 lines;
`run_cmd`'s four call sites (`tools.rs:2151`, `tools.rs:2566`, `adopt.rs:622`, `verification/product.rs:255`);
`migrations/executor.rs:714` inside `#[cfg(test)]` beginning at line 665; all 23 non-test `.class()` sites and the
22 that remain after excluding the comparison machinery; `PathDecision`'s single literal construction site
(`paths.rs:710`) by grepping every `.rs` file at `35461c9`; `RepositoryContract`'s four fields;
`PolicySet::load`'s `kernel_dir = trust.policy_root` and its authentication contract at `policy.rs:112-117`;
`repository_contract_baseline` as a local at `policy.rs:410`; `adopt.rs:1579/1585`'s unfloored `{d}/**`
generation; `memory/profile.rs::shebang` in full, including the `parts.find(|a| !a.starts_with('-'))` `env` case
that returns `"PATH=."` for `-S`; and `profile.rs:19`'s "content-hashed" interpreter claim.

Both probes ran unprivileged and wrote only inside the session scratchpad
(`/tmp/claude-1000/…/scratchpad/p2syn/`, `…/scratchpad/fdexec*`). **No repository file was created, modified or
deleted by this synthesis other than this document.** Residue disclosed for honesty: the scratchpad retains
`p2syn/{true,install.sh,decoy/install.sh,fdexec_script.sh}` and the compiled `fdexec` binary, all outside the
repository.

**Source claims re-derived rather than inherited:** `t2.rs` (`SEALED_RECORD_TYPES`, `verify_file`,
`classify_path`, the symmetric-key limitation); `cit/binding.rs` (the `os_state` manifest); `human_channel.rs`
(Ed25519, key off-machine, use-time re-verification); `capabilities/binding.rs` (`LOADER_ENV_VARS` = 30 entries,
no `PATH`); `util.rs::run_cmd` (no `env_clear`, program by string); `tools.rs` (the kernel-floor concession;
`skip_wrappers` at `35461c9:981-1000`); `policy_precedence.rs` at `35461c9` (`path_rule_narrowing`,
`overlap_is_no_less_restrictive`, `evaluate_path_rules{,_overlay}`, and the function-span line counts);
`paths.rs` (`Exemption` = 2 variants); every `.class()` call site at `35461c9`;
`framework/schemas/repository-contract.schema.json` (no top-level `additionalProperties`; `paths.items`
`additionalProperties: false`; `class` enum = 14 values); `framework/schemas/tool.schema.json` (`pinned_files`
absent, no top-level `additionalProperties`); `TOOL_POLICY.yaml` enumeration counts at `35461c9`;
`framework/overlay-templates/REPOSITORY_CONTRACT.yaml` (the `owner_role`/`mutation` floor/local axis).
