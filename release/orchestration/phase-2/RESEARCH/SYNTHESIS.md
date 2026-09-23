# Trust-architecture prior-art study — synthesis

| Field | Value |
|---|---|
| Run id | **P2-SYN-0001** (architecture synthesiser) |
| Date | 2026-09-23 |
| Nature | **READ-ONLY.** One document written. No product, runtime, kernel, policy, schema or test file touched. Nothing implemented. Nothing decided on the owner's behalf. |
| Inputs | `COMMON-BRIEF.md`; `ORCHESTRATOR-MEASURED-ENVIRONMENT.md`; `AGENT-1`…`AGENT-6`; `PHASE_2_OPTION_B_ESCALATION_PACKAGE.md`; `AGENT_RUNS/P2-AR-0079.run.yaml`; OD-P2-03, OC-P2-04, OD-P2-05, OD-P2-07; `PHASE-2-FROZEN-GATE-CONTRACT.md`; Contract v3; `docs/DECISIONS.md` (D-0007, D-0009, ARCH-0003) |
| Trees read | working tree at `4d42c34` (`release/4.1.6-rc1`) **and** the frozen reviewed tree `35461c9` (`phase2/remediation-ac-review`). Where they differ it is stated; the A+C remediation exists **only** on `35461c9` and is not on the release branch. |
| Evidence added | two probes run on this machine (§1.2, §9.3). Both wrote only into the session scratchpad. |

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
> (same account) and could compute a seal. Against that attacker the primitive is **detection-grade, not proof**."*

The lower-trust party in this deployment profile is *an AI agent running on the owner's machine under the owner's
account*. That is exactly the attacker the module names. **Therefore: sealing the path map, by itself, is
detection-grade against the actual adversary, not proof.** Anyone who tells the owner that sealing "closes"
Property C without that sentence has overclaimed.

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

**(a) There is exactly one chokepoint, not twelve unknown consumers. [verified]** The review flagged "12 further
`.class()` consumers … outside the table," and OD-P2-07 demanded "search for ALL consumers." I enumerated every
`.class()` call site at `35461c9`. In production code — excluding tests and excluding the comparison machinery
itself — **every single one reads `contract().decide(path).class()`**:

```
cit/materiality.rs:870        context/receipt.rs:462,671     memory/integrity.rs:310
memory/indexer.rs (6 sites)   memory/manifest.rs:234         migrations/executor.rs:714
orchestration/tasks.rs:954,1882   paths.rs:346,445           verification/lineage.rs:295,596,981,1077,1082
verification/reporting.rs:682
```

`RepositoryContract::decide` is a single function that every class-derived authority effect flows through.
**Property C is a change to one function, not an enumeration over consumers.** That is the "one derived authority
source replacing several synchronised enumerations" the brief asks for — and it is already structurally available.
Agent 2's recommendation (§6) converges on this without having established it; I am recording it as verified fact.

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
**2 of the ~19 distinct authority effects** reachable from `decide().class()`.

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
| **Agent 4** | Landlock is the one REQUIRED-NOW-defensible candidate | **Accept the measurement, decline the priority.** Agent 4's honesty about P79-F11 is exactly right and I am amplifying it. Landlock closes AR77-F1/F2/F4 — which are `MEDIUM` and already disclosed under OD-P2-05 as "effects OD-P2-05 already declares unbounded." It closes **neither open HIGH**. Adopting a kernel LSM to close two MEDIUMs while two HIGHs stay open is priority inversion. → **USEFUL LATER / R2** (§13). |
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
| **P79-F8** `{pattern: product/*.py, class: test}` | HIGH | **YES** | `cit::materiality:870` reads `decide(path).class()`. Under floor-composition, `product/app.py` is matched by the kernel rule `product/**`, so its class comes from the kernel rules only. The appended project rule cannot change it. The obligation is never lost. |
| **P79-F9** same edit escapes lineage W7 | HIGH-adj | **YES** | `lineage.rs:981` filters on `CODE_CLASSES.contains(decide(rel).class())` — same chokepoint, same fix. |
| **AR77-F3** second consumer of `class` | closed | **YES, and structurally** | The class a consumer sees is floor-owned wherever a kernel rule matches, so a *future* unknown consumer inherits the property without being enumerated. This is the specific thing OD-P2-07 C asked for. |
| **P79-F10** "no mechanism exists" | MEDIUM | **N/A — the finding is false** (§1.1) | Three mechanisms exist. R uses two of them. |
| **AR77-F1** empty-authority `file://` | MEDIUM | **NO** | The write is performed by the *spawned process*, correctly executing verified bytes. R establishes identity, not effects. Closed only by §9.4 (Landlock) or by the governed review, which OD-P2-05 cl.4 already assigns. **State this plainly; do not let R be sold as closing it.** |
| **AR77-F2** absolute path inside a token | MEDIUM | **NO** | Same. |
| **AR77-F4** hard link | MEDIUM | **NO** | Same, and worse: `openat2`'s `RESOLVE_BENEATH`/`RESOLVE_NO_SYMLINKS` explicitly do not cover hard links — there is nothing to canonicalise. Only an inode/device boundary check or kernel confinement reaches it. |
| **P79-F3b** decoupled scan can remove a finding | LOW | **NO** | Untouched. It is a reporting-accuracy defect, correctly graded, and should stay on the register. |
| **R0/R1 unauthenticated-source attacks** | — | **NO, and R must not claim to** | Level 1. Answered to the accepted extent by SRR-1's verify-then-install transaction and monotonic high-water marks; the residual is the *frozen* RoT-1 question. R touches nothing here. §14. |

**Score, stated without spin: R closes 4 of 4 open HIGHs (P79-F1, F8, F9, F11) plus F12 and the AR68/AR73 class.
It closes 0 of the 3 open MEDIUMs (AR77-F1/F2/F4) and 0 Level-1 findings.** That is the honest boundary, and it
matches the partition in §1.4 exactly — which is a consistency check, not a coincidence.

## 6. USE DIRECTLY / WRAP / ADAPT / BUILD CUSTOM

Consolidated across all six researchers, adjudicated, with the brief's burden of proof on `BUILD CUSTOM`.

| Candidate | Class | Bucket | Note |
|---|---|---|---|
| `execveat(2)` / `fexecve(3)` | **USE DIRECTLY** | NOW | Measured working here for binaries *and* `#!` scripts (§9.3) |
| `O_PATH` + `O_NOFOLLOW` descriptor acquisition | **USE DIRECTLY** | NOW | correct way to obtain the fd |
| `nix` crate (`unistd::{execve,execveat,fexecve}`) | **WRAP** | NOW | MIT, actively released; `std` has no descriptor-exec at all |
| `std::process::Command` `env_clear`/`current_dir` | **USE DIRECTLY** | NOW | necessary hygiene; **not sufficient** (§1.2) |
| Bazel fixed-`PATH` + `--action_env` allowlist | **ADAPT** | NOW | hangs off the existing `tool.schema.json` declaration surface |
| Chen/Wagner/Dean erase-and-allowlist | **ADAPT** | NOW | supersedes the 32-entry `LOADER_ENV_VARS` denylist (§8) |
| `t2::seal_value` / `verify_file` / `classify_path` | **USE DIRECTLY (in-repo)** | NOW | detection-grade; see §1.1 caveat |
| `human_channel` owner signature (Ed25519, key off-machine) | **USE DIRECTLY (in-repo)** | NOW | the only *proof*-grade authority anchor available |
| `cit::binding` `os_state` manifest shape | **ADAPT (in-repo)** | NOW | the already-proven action manifest (§2) |
| SELinux `neverallow` — semantic check over expanded state | **ADAPT** | NOW | the pattern behind floor-composition |
| OPA multi-bundle AND-composition | **ADAPT** | NOW | the operator, not the engine |
| Object-capability discipline (Hardy '88, Miller '06) | **ADAPT (vocabulary + audit method)** | NOW | free; prevents re-enumeration |
| Saltzer & Schroeder complete mediation | **ADAPT** | NOW | the oldest correct statement of the defect |
| Floor-composed `decide()` | **BUILD CUSTOM** | NOW | **Justified**: ~40 lines inside an existing function, reusing the existing kernel-template baseline and the existing `owner_role`/`mutation` axis. No external primitive expresses "this project's path map" |
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

**Only one `BUILD CUSTOM` survives**, and it is ~40 lines inside a function that already exists. That is the
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

Also deleted: **`LOADER_ENV_VARS`, 32 entries** (`runtime/src/capabilities/binding.rs`), replaced by
`env_clear()` + a fixed `PATH` + a declared allowlist. Worth noting why this list is itself evidence: it is the
product's *best* existing environment defence and **it is a denylist that does not contain `PATH`, `IFS` or
`GIT_SSH_COMMAND`** **[verified]**. The mechanism BC-P2-40 built to stop code substitution omits the variable that
P79-F1 uses. Erase-and-allowlist is not a refinement of this; it is its replacement.

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
| `CLASS_EXEMPTIONS` table | 30 |
| `rule_effective_attrs` | 16 |
| `describe_exemptions` | 13 |
| `Exemption` enum | 10 |
| `class_exemptions` | 7 |
| `class_confers`, `patterns_may_overlap` | 6 |
| **total** | **457** |

Floor-composition replaces the **comparison** — roughly 300 of those lines — with a second `decide()` pass over
the kernel rules and a field-wise AND (~40 lines). The **reporting** (~130 lines of applied/refused records that
OC-P2-04 §2 and §4 require, feeding `gov policy overrides` and doctor D027) is **retained**, not deleted. Net
≈ **−260 lines of hand-written security comparison logic**, and the `Exemption` vocabulary disappears entirely.

**Reductions in the brief's own terms:**

| Metric | Before | After |
|---|---|---|
| Authority sources for `class` | project file, with the kernel template consulted *comparatively* | one: the kernel rules decide any path they match |
| Enumerations that must be kept complete | 45 exec-semantics entries + 32 loader vars + 2 exemptions + 14 class values × 19 effects | **0** for execution semantics; **0** for class authority |
| Custom security comparison code | 457 lines | ≈130 (reporting only) |
| Consumers that must be found and updated | feared 12+; **actually 1** (`decide()`) — §1.3a | 1, and now correct by construction |
| Proof surface | "did we enumerate every shape / every consumer?" (unbounded, unfalsifiable) | "does `decide()` return the floor where a kernel rule matches?" + "is the exec'd fd the hashed fd?" (two bounded, testable propositions) |
| TCB | + the classifier's semantic model of every shell/interpreter on earth | + two syscalls already in the kernel |

**The most important deletion is not a line count.** It is that both remaining propositions are **falsifiable by a
single test each**, whereas "have we enumerated everything?" has been unfalsifiable for five rounds — which is
precisely why five rounds each ended with a reviewer finding one more.

## 9. Recommended architecture — Problem A (execution trust)

### 9.1 The property

> **The OS executes a kernel object it holds, never a name it was handed.** Verification produces a
> `ResolvedExecution`; execution consumes only that; nothing in between re-derives any part of it.

### 9.2 The shape, in four obligations

1. **Reduce, do not classify.** For each declared command, the OS attempts to reduce it to a
   `ResolvedExecution { interpreter: Option<Fd>, artefact: Fd, argv: Vec<OsString>, envp: Vec<OsString>, cwd:
   AbsPath }` where every `Fd` was obtained by the OS from an absolute canonical path and hashed **through that
   descriptor**. **If the reduction fails for any reason, the command is `undetermined` and gates** — OD-P2-05
   clause 3 unchanged. A wrapper program is a reduction failure, not a token to skip. *This is the limb §1.2
   proves is load-bearing.*
2. **Execute the object.** `execveat(artefact_fd, "", argv, envp, AT_EMPTY_PATH)`, with the interpreter's own
   descriptor when the artefact is a script and the descriptor **not** opened `O_CLOEXEC` (§9.3).
3. **Construct the environment; do not filter it.** `env_clear()`, then a fixed OS-owned
   `PATH=/usr/bin:/bin` (Bazel's shipped default since 0.21), a disposable OS-owned `HOME`, and an explicit
   per-tool allowlist. The natural home is the existing `tool.schema.json` declaration surface, which already
   carries `permissions`, `required_permission_classes`, `capabilities`, `credential_scope`, `version_pin` and
   `installation_sha256` — this answers Agent 3's one open obstacle.
4. **Re-verify at every execution.** Re-open, re-hash, re-exec per invocation — OD-P2-05 clause 5, unchanged in
   requirement, now cheap because hash and exec share one descriptor.

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
2. **One chokepoint, therefore no consumer enumeration.** All ~19 production consumers already read
   `decide().class()` **[verified §1.3a]**. OD-P2-07 C's "search for ALL consumers" is discharged by a
   *structural* argument rather than a search, which is strictly stronger and is the thing four previous rounds
   could not achieve.
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

### 10.4 The limit of this fix, which the challenger will find if I do not state it

**The floor's coverage equals the kernel template's coverage.** The template covers `governance/**`, `spec/**`,
`product/**`, `archive/**`, `**/.env*`, `**/secrets/**`, `.governance-runtime/**`, `.governance-state/**`. A
project whose product lives at `src/` or `app/` has **no floor for it** — and `adopt.rs` generates native-layout
rules for exactly such projects. For those paths, class remains project-owned, and P79-F8's *shape* remains
available even though its *instance* is closed.

This is structurally the same finding as the RoT-1 review's "64 of 125 leaves unfloored," recurring here. It is
not a reason to reject floor-composition — it is a reason to state its scope precisely, to make "this path is
unfloored" **observable** in `gov policy overrides` and doctor, and to put "should the floor be extended to
declared project roots?" on the owner's list (§16, Q3). Anything that presents floor-composition as total is
overclaiming.

## 11. The smallest thing that closes the two open HIGHs — and how it differs from the architecture

The brief asked for this separation explicitly, and it matters because the owner may want the minimum.

**The minimum, for both open HIGH classes:**

| # | Change | Closes | Size |
|---|---|---|---|
| 1 | In the installation classifier, treat a **wrapper program as a reduction failure** (`undetermined` ⇒ gate) instead of a prefix to skip. Delete `skip_wrappers` and `wrapper_programs`. | **P79-F11, P79-F12, P79-F1** | one function deleted, one branch changed |
| 2 | Exec the **resolved absolute artefact** (and resolved absolute interpreter), with `env_clear()` + fixed `PATH`, at `util::run_cmd`'s two install call sites. | hardens 1; closes the residual `PATH` shapes | ~20 lines |
| 3 | In `RepositoryContract::decide`, take **`class` from the kernel rules** wherever a kernel rule matches. | **P79-F8, P79-F9**, and AR77-F3 structurally | ~40 lines |

**That is it. Three changes, no new dependency, no new crate, no kernel feature, no schema change.** Measured
T1/T2/T3 say change 1 is the one that actually matters for A, and §1.3(a) says change 3 needs no consumer sweep.

**What the minimum is *not*:**

- It is **not** descriptor-based execution. Change 2 closes the *identity-rebinding* attacks that exist today;
  `execveat` closes the *TOCTOU window* between hash and exec, which is a narrower, un-demonstrated residual. Add
  it when implementing the architecture, not to close the HIGHs.
- It is **not** the T2 seal on the path map. Floor-composition alone makes P79-F8 inert. The seal adds
  observability (OC-P2-04 §4) and catches shapes outside the floor's coverage (§10.4).
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
| **Landlock** | **3, used as a 2B compensating control** | **Contaminating if placed in REQUIRED NOW.** It is a kernel LSM security boundary. Agent 4 argued both sides honestly and declined to make the call; I am making it: **R2, not now.** It closes no open HIGH (§5), and pulling a Level-3 mechanism into a stopped Phase 2 to close two already-disclosed MEDIUMs is precisely "solving an R3 problem inside Phase 2 because the technology exists." |
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
3. **`argv` handed to a pinned artefact is still attacker-influenced.** §9 binds *which bytes run*. It does not
   bind what the artefact is told to do. A project that pins `/usr/bin/env` as its artefact reconstructs P79-F1
   inside a "conforming" install. **The reduction must refuse to admit a program whose documented job is to
   re-execute another program** — and that boundary is itself a judgement, i.e. a small residual enumeration
   moved from "what can this command do" to "is this artefact an exec vector." Smaller and bounded, but not zero.
   I flag it because it is the likeliest place a sixth round would be found.
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

1. **Is the corrected Property-A recommendation authorised?** §1.2 falsifies what the escalation package proposed.
   The owner has not yet been asked to authorise "do not execute wrapper chains" — which is a *behaviour change*
   for projects whose installers legitimately use `env`, `nohup` or `timeout`. **This is the one question that
   must be answered before any work starts.**
2. **Is detection-grade acceptable for the path-map seal?** Given §1.1's key exposure, does the owner accept
   detection-grade integrity for authority-bearing config, with proof-grade reserved for the owner-signed gate
   route? (This is the question Agent 2 correctly declined to answer.)
3. **Should the floor extend beyond the kernel template's path coverage?** §10.4: projects with a non-standard
   layout have unfloored authority-bearing paths. Extending the floor to adopted project roots is a product
   decision about what "project-editable" means.
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

---

# PART V — THE OPTIONS

Three coherent architectures, ranked. Not a catalogue: each is a complete position, and each strictly contains the
one above it.

## OPTION 1 — **Resolve once, execute the object; floor the class** *(recommended)*

| | |
|---|---|
| **Existing technology / pattern used** | `execveat(2)`/`O_PATH` (kernel, **measured working here** for binaries and `#!` scripts); `std::process::Command` `env_clear`; Bazel's fixed-`PATH` + `--action_env` allowlist (shipped default since 0.21); Chen/Wagner/Dean 2002 erase-and-allowlist; SELinux `neverallow` semantic-closure check; OPA multi-bundle AND-composition; **in-repo**: `t2::seal_value`/`verify_file`/`classify_path`, `human_channel` Ed25519 owner signature, and `cit::binding`'s already-proven action-manifest shape. |
| **What Governance OS still has to build** | A `ResolvedExecution` reduction (wrapper ⇒ `undetermined`) at the two `util::run_cmd` install sites; descriptor acquisition + hash-through-fd + `execveat`; a constructed `envp` hanging off `tool.schema.json`; floor-composition inside `RepositoryContract::decide` (~40 lines); `"repository-contract"` added to `SEALED_RECORD_TYPES`; an owner-gated route for legitimate class widening. **One `BUILD CUSTOM`, ~40 lines, inside an existing function.** |
| **Assurance achieved** | Closes **all 4 open HIGHs** (P79-F1, F8, F9, F11) + F12 + the AR68/AR73 class. Property A's guarantee is *falsifiable by one test* ("is the exec'd fd the hashed fd?") rather than by an unbounded enumeration. Property C's guarantee is *structural* ("does `decide()` return the floor?"), discharging OD-P2-07 C's "find all consumers" by construction. **Does not close AR77-F1/F2/F4** (effects) or anything at Level 1. |
| **Complexity** | Low. Two call sites for A, one function for C. No new crate for the §11 minimum; one small crate (`nix`) for the descriptor-exec increment. |
| **Likely effort** | §11 minimum: small — three changes, no dependency. Full Option 1 with descriptor-exec, the seal and the owner-gated route: moderate, dominated by test/negative-control authoring (including the `O_CLOEXEC` control) and by the workflow design for Q4, not by the code. |
| **Effect on the TCB** | **Net reduction.** Removes the classifier's semantic model of shells and interpreters (45 policy entries + `skip_wrappers`), the 32-entry loader denylist, and ~260 lines of comparison logic. Adds two syscalls in a kernel already trusted. The `landlock`/bubblewrap/container TCB is *not* added. |
| **Effect on Phase-2 acceptance** | Directly addresses both OD-P2-07 limbs at the level the owner asked ("remove the pattern, not another enumeration"). Positive for **AC-3** (the remaining PARTIALs get *argued* rather than *enumerated* justifications) and **AC-4**. Neutral to **AC-14** — it changes `product_code_digest`, so R1 re-verification is required either way. Leaves AR77-F1/F2/F4 as disclosed residual, which is where OD-P2-05 clause 4 already placed them. |
| **R2 path** | Add Landlock for the effects residual; add `memfd_create` sealing for staged content; schema-constrain `pinned_files`; in-toto Statement shape for evidence digests. Each is additive. |
| **R3 path** | Unchanged and unblocked: bubblewrap → rootless containers → gVisor/microVM, in that order, if the profile ever becomes multi-tenant. Option 1 does not foreclose any of it. |
| **Reversibility** | **High, and this is its second-strongest property.** A is two call sites and a policy-list deletion; reverting restores the lists from git. C is one function plus one string in a three-member const; reverting restores comparison. The seal is additive (a top-level field the schema already permits). The owner-signed route is a new gate, removable. **No data migration, no format change, no external dependency to unwind, no schema change.** |

**The case against, stated fairly:** it does not close AR77-F1/F2/F4, so a reviewer who regards those as the real
remaining risk will find Option 1 incomplete. It also leaves assumption 3 (§15) as a small, bounded residual
judgement — "is this artefact an exec vector" — which is the one place a sixth round could still be found.

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

**1 › 2 › 3.** Option 1 closes every open HIGH, deletes more than it adds, needs no new dependency for its
minimum, and is reversible in an afternoon. Option 2 is its correct R2 successor. Option 3 is a genuine
architecture whose time is not now and which needs Option 1 inside it regardless.

If only one sentence reaches the owner, it should be this:

> **The recommended Property-A fix would not have worked — measured, on this machine — and the Property-C
> prerequisite the owner was told to settle first does not exist; both problems reduce to the same three
> changes, and none of them needs a new dependency.**

---

## Appendix — evidence I produced in this session

**Probe 1, §1.2** (`scratchpad/p2syn-probe.sh`): P79-F1 and P79-F11 attempted under `env -i
PATH=/usr/bin:/bin` with cwd pinned to the project root. Both succeeded; the wrapper-free control ran the verified
bytes. GNU coreutils 9.4, kernel 6.6.87.2-microsoft-standard-WSL2.

**Probe 2, §9.3** (`scratchpad/fdexec.c`): `execveat(fd,"",AT_EMPTY_PATH)` on a binary → success; on a `#!`
script → success; with `O_CLOEXEC` → `ENOENT`; `/dev/fd` and `/proc/self/fd` present.

Both probes ran unprivileged and wrote only inside the session scratchpad
(`/tmp/claude-1000/…/scratchpad/p2syn/`, `…/scratchpad/fdexec*`). **No repository file was created, modified or
deleted by this synthesis other than this document.** Residue disclosed for honesty: the scratchpad retains
`p2syn/{true,install.sh,decoy/install.sh,fdexec_script.sh}` and the compiled `fdexec` binary, all outside the
repository.

**Source claims re-derived rather than inherited:** `t2.rs` (`SEALED_RECORD_TYPES`, `verify_file`,
`classify_path`, the symmetric-key limitation); `cit/binding.rs` (the `os_state` manifest); `human_channel.rs`
(Ed25519, key off-machine, use-time re-verification); `capabilities/binding.rs` (`LOADER_ENV_VARS` = 32 entries,
no `PATH`); `util.rs::run_cmd` (no `env_clear`, program by string); `tools.rs` (the kernel-floor concession;
`skip_wrappers` at `35461c9:981-1000`); `policy_precedence.rs` at `35461c9` (`path_rule_narrowing`,
`overlap_is_no_less_restrictive`, `evaluate_path_rules{,_overlay}`, and the function-span line counts);
`paths.rs` (`Exemption` = 2 variants); every `.class()` call site at `35461c9`;
`framework/schemas/repository-contract.schema.json` (no top-level `additionalProperties`; `paths.items`
`additionalProperties: false`; `class` enum = 14 values); `framework/schemas/tool.schema.json` (`pinned_files`
absent, no top-level `additionalProperties`); `TOOL_POLICY.yaml` enumeration counts at `35461c9`;
`framework/overlay-templates/REPOSITORY_CONTRACT.yaml` (the `owner_role`/`mutation` floor/local axis).
