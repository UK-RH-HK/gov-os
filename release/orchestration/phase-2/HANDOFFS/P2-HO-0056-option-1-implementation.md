# P2-HO-0056 — Option 1 implementation (OD-P2-08)

| Field | Value |
|---|---|
| Authorised by | **OD-P2-08**, the owner's Phase-2 completion decision, 2026-09-23 |
| Base | `phase2/remediation-ac` `35461c9` (full suite 263/0) |
| Execution | native Claude subagent, `claude-sonnet-5`, worktree-isolated |
| Evidence class | **`BUILDER_DEVELOPMENT_EVIDENCE`** — nothing you write can close a finding |
| Next | one full suite → freeze → fresh Opus 5 adversarial review with independently derived held-out probes |

## 1. What you are building, and what you must not

You implement **Option 1: "resolve once, execute the object; floor the class."** The owner accepts the research
diagnosis that every previous failure was a **confused-deputy / ambient-authority** problem — *the check reasons about
a representation while the authority or effect is determined outside it.*

> **Remove ambient authority. Do not extend lists of programs, flags, command shapes, class values or consumers.**

Six rounds have failed by enumeration. **If you find yourself adding a name to a list, you are doing the wrong thing.**

## 2. Property A — resolved execution

> **The OS executes a kernel object it holds, never a name it was handed — and nothing inside that object may silently
> name a second unverified executable object before the first reviewed instruction.**

Build a `ResolvedExecution` reduction covering **three** resolution layers. All three are measured, not theoretical —
each defeated a previous fix.

### 2a. The command itself

Execute the **resolved object**, not the name. Prefer resolved absolute identity, `O_PATH`-held descriptors, and
`execveat`-style execute-the-held-object. Construct the environment; inherit no ambient `PATH` or loader authority.

**Wrapper chains do not qualify for the ungated path** (OD-P2-08 §3). `env`, `nohup`, `timeout`, shell wrappers,
interpreter wrappers and opaque chains cannot claim *"the exact reviewed artefact is necessarily what executes"* unless
the complete executable closure is resolved and verified. Otherwise `UNDETERMINED` → governed route. Expect
`skip_wrappers`/`wrapper_programs` to be **deleted**; the inverted default already gates.

**Measured, so you know why**: under a *fully cleared* environment with cwd pinned, `env --chdir=decoy sh install.sh`
still ran the decoy and `env PATH=. true` still ran a project-local binary. Environment control alone does nothing —
`env` is a *program*, and those are its *arguments*.

### 2b. The shebang closure

**Measured**: a hash-pinned artefact beginning `#!./w` ran an unpinned project file — and the control proves the attack
**required the cwd the OS itself pinned**. `#!/usr/bin/env -S PATH=. sh` discarded the constructed environment one exec
hop later.

A script reaches the ungated path only where the interpreter reduces to verified objects: an **absolute** interpreter
resolved, opened and verified **inside the same `ResolvedExecution`**. A relative interpreter, an `env`-fronted
shebang, or `-S`/other re-exec indirection is a **reduction failure** unless structurally reducible. **Not by a flag
list.**

`runtime/src/memory/profile.rs:378 fn shebang` exists and is **itself defeated by `-S`** (it returns `"PATH=."` as the
interpreter). Reuse it; do not reuse it unchanged.

### 2c. The dynamic-dependency closure — new, from probe P2

**Measured this session** (`RESEARCH/P2-LOADER-PROBE.md`, read it): a pinned dynamically-linked ELF with
`RUNPATH: [$ORIGIN]` ran **`UNVERIFIED-CODE-RAN-BEFORE-MAIN`** and wrote a file outside the project root — under a
**fully cleared environment**, with the pinned artefact's hash **byte-identical before and after**. `RUNPATH` lives
*inside the ELF*, so environment hygiene cannot reach it.

The rule, which names nothing:

> An ELF artefact's closure **includes its dynamic-dependency closure**. Resolve `DT_NEEDED` as the loader will
> (`RUNPATH`/`RPATH` with `$ORIGIN` expansion, then system paths); **open, verify and bind every resolved object**, or
> the execution is `UNDETERMINED`.

Measured consequences: a **static** artefact has `0` dynamic entries — its closure is itself. An artefact resolving
only from authenticated system paths inherits the machine floor. One whose resolution reaches **project-controlled**
paths carries those objects in its closure.

**State your guarantee precisely**: *"every executable object the kernel and dynamic loader resolve before the first
reviewed instruction."* What a verified interpreter subsequently *imports* (`PYTHONPATH`, `NODE_PATH`) is **outside**
this property and belongs to OD-P2-05 clause 4's independent review. Say so rather than implying more.

## 3. Property C — floor composition

```
authenticated Project Adoption Floor + applicable kernel floor + project-local additions/narrowing
        ↓  one authoritative construction point
   Effective PathDecision
```

**`class` is not an ordered level. Do not build a bidirectional more/less-privileged predicate** — it is impossible;
`source` and `test` are not orderable. It is a semantic label whose obligations differ by context.

**The floor is PROJECT-SPECIFIC (OD-P2-08 §2).** Governance OS governs exactly the adopted repository and imposes **no
universal layout**. `src/**`, `backend/**`, `services/**`, `app/**`, `packages/**` are all legitimate; **no universal
`product/**` assumption may be required**. This closes precondition P1: `adopt.rs:1579/1585` currently generates
*unfloored* rules for non-`product/` layouts, and that is the gap — the floor must be derived from the repository's
**actual native structure** during governed adoption, and authenticated by that transition.

Project-local layers may add, narrow or strengthen. They **must not silently remove obligations** from the
authenticated floor. Legitimate change to the floor runs: proposal → CIT/impact → Human Gate where required →
owner-authorised transition → new authenticated floor → evidence invalidation.

**Use type construction.** `PathDecision` is constructed at exactly one site (`paths.rs:710`); keeping it that way is
what makes OD-P2-07 C decidable rather than an unfalsifiable search.

**Observability is required (OC-P2-04 §4 — silence is failure).** The system must clearly report: a floored path, a
project-added rule, a governed widening, an **unfloored path where legitimate**, and a refused attempted weakening.

## 4. Reuse, not reinvention

**Do not build a hand-edit detector.** `cit::binding` already implements the governed-versus-hand-edited pattern bound
to owner-signed Human Decision Gate evidence. Use that architecture.

**The T2 seal is detection, not proof.** Its key is symmetric and readable by any process with the owner's OS
privileges — and its own module notes a forgery is honoured on the owner's *other* machines. `"repository-contract"`
may join `SEALED_RECORD_TYPES` as defence in depth, but **proof-grade authority is the authenticated machine/kernel
floor + the authenticated project adoption floor + an owner-signed governed transition.**

**Close the `pinned_files` schema gap**: it appears 7 times in `tools.rs` and **0 times** in `tool.schema.json`, which
sets no top-level `additionalProperties`. Make the representation explicit so malformed structure cannot silently
acquire meaning and runtime agrees with schema. **Not a broader schema redesign.**

## 5. Do not implement

**Landlock** (R2), **hermetic execution**, **bubblewrap / containers / gVisor / microVMs** (R3). Not because they are
wrong — because they close no open HIGH and the target is the private local machine.

## 6. Your tests are development evidence only

OD-P2-08 §7: builder-authored tests are regression evidence — **including property and generative tests**. *A
generative test is not independent merely because it generates many cases.* A fresh reviewer will independently derive
the property, the attack domain, **the generator domain**, and both control sets.

This is not hypothetical: the last round's test was named `..._for_any_class_value_...` and quantified over exactly the
two values its author implemented.

**So: name the cases your generators cannot reach.** The last two builders did this unprompted and it was the most
valuable part of both handovers.

## 7. Sequence and testing

Targeted tests → affected dependency tests → deterministic build/schema checks → **one** full certification run.

- The full suite costs **~50 minutes** (measured: 263 tests, 3,084 s, machine-exclusive, default threads). The ~20–24
  minute figure is **retracted**.
- **Never `--test-threads=1`.** Never pipe a test command without `set -o pipefail`. Never run bare `cargo fmt` (it
  reformats outside your scope). Start commands with `. "$HOME/.cargo/env"`.
- Record with every suite figure: exact command, commit, test count, thread setting, machine load, duration, outcome.

**You are pre-authorised to change what existing tests assert** where Option 1 makes their old claim false — same
conditions as before: **no renames**, every changed assertion listed with old and new claim, never weakened to pass,
and if a test cannot be satisfied by a *correct* implementation, stop and report it.

## 8. Anti-stall — you must never wait on me

`worker_stall_protection` is ACTIVE with 13 rules. **Do not ask permission to start your full suite.** Evaluate the
precondition yourself: proceed when no competing `cargo`/`gov` process runs and load is below ~4; otherwise wait,
re-check, and **proceed automatically**.

Every wait you write needs a **bounded iteration count** and a **deterministic timeout action**. If you use process
matching, **prove the waiter cannot match itself** — a `pgrep -f <pattern>` inside a shell whose command line contains
that pattern never exits, which cost this orchestration ten hours.

If you genuinely need a decision, report `BLOCKED_ON_COORDINATOR` with why, what you await, a timeout, and the default
action you will then take — and take it.

Checkpoint to `telemetry/checkpoints/P2-AR-0080.checkpoint.md` before the full suite and after each property lands.

## 9. Return

Verdict, then: what mechanism enforces each property and **what you deleted**; the three closure layers with how each
is enforced; how the project-specific floor is derived and authenticated at adoption; the `PathDecision` construction
point; observability per OC-P2-04; the `pinned_files` schema change; changed test assertions with old and new claims;
tests added with kinds; **the cases your generators cannot reach**; checks run with command/commit/count/threads/load/
duration; anything left undone; and your commit SHA.

An accurate `PARTIAL` naming a real weakness is worth far more than a confident `REPAIRED_CLAIMED`. The reviewer that
follows you is independent, adversarial, and has broken this surface at every level it has been secured — argv,
wrapper arguments, shebang, and now the dynamic loader.
