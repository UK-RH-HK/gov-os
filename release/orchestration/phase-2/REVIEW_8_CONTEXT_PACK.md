# Review-8 whole-system context pack

| Field | Value |
|---|---|
| Required by | **OD-P2-10 §1** — a mandatory step between the pre-final owner sweep and Review 8 |
| Purpose | *"Independence must mean independent reasoning **plus complete relevant context**, not independent reasoning plus architectural ignorance."* (OD-P2-10 §4) |
| Principle | **Complete relevance, not complete repository loading** (OD-P2-10 §11). This is a bounded packet, not a repository dump. |
| Status of §9 | **PENDING** until P2-AR-0096 reports; every other section is final. |

> **This pack tells you what exists and why. It does not tell you what to conclude.** You derive your own attacks,
> properties, generator domains and controls. Where this pack states a measurement, it names who measured it so you
> can re-run it rather than trust it.

---

## 1. Product purpose → what Phase 2 actually claims

Governance OS governs **exactly the repository into which it is adopted**. It is a Rust runtime (`runtime/`) plus a
CLI (`cli/`, the `gov` binary) that constrains how agents and humans change that repository: what may execute, what
each path obliges, which transitions need owner authority, and what evidence is required.

Phase 2's terminal state is `GOVERNANCE_CAPABILITY_BASELINE_ACCEPTED`. It claims a **capability baseline**, not
absolute security. The owner has stated the standard explicitly (OD-P2-09 §6):

```
defined private/local deployment boundary
+ Contract-v3 current-phase obligations satisfied
+ required properties independently evidenced
+ no known blocking HIGH
+ R0/R1 preserved
+ residual MEDIUM/LOW explicitly bounded and dispositioned
+ evidence fresh for the exact candidate
```

> It is **not** "no conceivable defect can ever be found in future." A competent reviewer finding a LOW or MEDIUM
> observation does not make the architecture unfit.

## 2. Deployment profile — and what is deliberately out of scope

Owner-controlled WSL/Linux machine; private repositories; **one owner**; OS/admin/hardware trust assumptions
explicit; models, agents and projects are **lower-trust than Governance OS authority**; no public SaaS; no hostile
multi-tenant environment.

**Deferred by owner decision, not oversight** (OD-P2-08 §6, OD-P2-09 §7): Landlock effect containment (R2); full
hermetic execution; bubblewrap, rootless containers, gVisor, microVMs (R3); high-assurance supply-chain ceremony; the
R3 multi-tenant threat model. *Do not introduce a Level-3 mechanism merely because it exists.* A finding that
**requires** one is a stop condition, not a repair.

**The threat actor this phase models:** an agent or process with **ordinary project-scoped write access** — it can
write any file inside the repository, including governance files, but cannot write the protected machine state root
and does not have the owner's `install_kernel` authority.

## 3. The two properties

### Property A — resolved execution

> The OS executes a kernel object it holds, never a name it was handed — and nothing inside that object may silently
> name a second unverified executable object before the first reviewed instruction.

**Status: CONVERGED.** Held under three consecutive fresh independent adversarial reviews (AR90, AR92, AR94).
`runtime/src/exec_resolve.rs` is **out of scope** (OD-P2-09 §3): confirm preservation, do not reopen settled design
without evidence.

It reached that state the hard way, through four successive defeats, and the sequence is the most useful thing to
know about this codebase: **argv → wrapper arguments → shebang → dynamic loader.** Each layer was secured, and each
time a *second resolution* was found one level below. The closure now covers the command itself, the shebang chain,
and the ELF dynamic-dependency closure (`DT_NEEDED` / `RUNPATH` / `RPATH` with `$ORIGIN`).

**Stated limit, deliberately:** the guarantee is *"every executable object the kernel and dynamic loader resolve
before the first reviewed instruction."* What a verified interpreter subsequently **imports** (`PYTHONPATH`,
`NODE_PATH`) is outside this property. Known-unprobed and recorded as such: `LD_AUDIT`/`ld.so.preload` at machine
scope, setuid/capability-bearing binaries, glibc+musl, malformed-ELF fuzzing, the `verify`→`Command` TOCTOU window.

### Property C — floor composition

```
authenticated Project Adoption Floor + applicable kernel floor + project-local additions/narrowing
        ↓  one authoritative construction point
   Effective PathDecision
```

**Status: where every failure has landed.** `class` is **not** an ordered security level and no bidirectional
more/less-privileged predicate may be built — `source` and `test` are not orderable. It is a semantic label whose
obligations differ by context.

## 4. Owner decisions in force — read these, they are normative

| Id | Settles |
|---|---|
| **OC-P2-04** | Project files may **narrow** but never **manufacture** authority. §4's five reportables: a floored path, a project-added rule, a governed widening, an unfloored path where legitimate, a refused weakening. **Silence is failure.** |
| **OD-P2-05** | Bind the bytes |
| **OD-P2-07** | A + C as one bounded structural remediation |
| **OD-P2-08** | Complete Phase 2 on Option 1. **P1 resolved: the floor is PROJECT-SPECIFIC** — no universal `product/**` assumption may be required. **T2/HMAC sealing is detection and defence in depth, NEVER proof-grade owner authority**, because its symmetric key is readable by any process with the owner's OS privileges. Proof-grade = authenticated machine/kernel floor + authenticated project adoption floor + owner-signed governed transition. *"Do not implement 'detect whether a human edited this file' as the trust model. Authenticate the authoritative transition instead."* |
| **OD-P2-09** | Review 8 is the **convergence decision point**. The simplification principle is binding: an optional/recovery feature that repeatedly produces HIGH findings is **deleted or simplified, not wrapped**. |
| **OD-P2-10** | This pack. Plus: if Review 8 fails with another blocking HIGH, the product **freezes** and a separate session builds a context/retrieval bridge before further repair. |

## 5. The trust model, stated plainly — this is where reviewers have most often had to guess

| Thing | Trust status |
|---|---|
| **Protected machine state** (`srr::state::resolve_state_root()` → `adoption-floors/`, `health-sandboxes/`) | **Proof-grade.** Outside every project. AR88 established an ordinary actor cannot write here. This is the anchor of Property C. |
| **Owner-signed governed transition** (`human_channel`, Ed25519; Human Decision Gates; CIT) | **Proof-grade.** |
| **Installed kernel floor** | **Proof-grade** (authenticated chain). |
| **T2 seal** (`t2::seal_value`, `mac_message`) | **Detection only.** Symmetric key, readable in the local OS trust domain. Its own module notes a forgery is honoured on the owner's *other* machines. `mac_message` binds **content only** — no path, no project, no record type. It has never been modified in this phase and must not be. |
| **`bound_repository_lineage`** (git lineage) | **Not proof of ownership.** Public and reproducible by cloning (AR86-C1); an in-repository actor can change it (`git checkout --orphan`, or moving `.git` aside). |
| **The floor document** (`governance/registry/project-adoption-floor.json`) | **An ordinary project file an attacker can write.** It may carry evidence; it must never carry authority. |
| **Environment variables** | **Ambient authority — never trusted for a decision.** |

**The recurring defect, in one sentence, and the thing most worth testing:**

> A check reasons about one representation while the real authority or effect is determined somewhere else.

## 6. Eight rounds of failure — the pattern, because it predicts where to look

| Review | Property A | Property C | Root causes |
|---|---|---|---|
| AR82 | fail | fail | systemic |
| AR84 | fail | fail | 6 HIGH |
| AR86 | fail | fail | 6 new (4 closed as a class) |
| AR88 | fail | fail | 11 |
| AR90 | **HOLDS** | fail | 1 idea |
| AR92 | **HOLDS** | fail | 2 (one conjunct, one path-shape) |
| AR94 | **HOLDS** | fail | 2 (both mechanisms AR93 had just added) |

Test count grew 263 → 274 → 289 → 300 → 319 → 337 → 350 → 363 → 373, green at every freeze.

**Every failure was an enumeration failure**: programs → command shapes → list premises → class values → consumers →
obligations → a liveness predicate on an attacker-chosen string → a capability outliving its subject, and a trusted
input read from a file the attacker can write.

**And the mechanism that kept it going:** each repair added a mechanism, and that new mechanism became the next
round's defect. AR91 added `other_live_claim`; AR92 broke exactly that. AR93 added `floor-reanchor` and a sandbox
marker; AR94 broke exactly those. **This is why the current round mostly deletes.**

## 7. What is settled and must not be reopened without evidence

* **Level 1 / R0 / R1** — SRR/RoT release authenticity, TUF-shaped metadata, signed roles, root rotation,
  rollback/high-water, Phase-1 bootstrap, R3 supply-chain assurance. A Phase-2 finding may require *proving* R1
  preservation; it must not silently reopen Level 1. Hard constraints:
  `multi_machine::clone_rebuilds_identical_derived_state` and `brownfield::brownfield_adoption_end_to_end`.
* **Property A / `exec_resolve.rs`** — see §3.
* **`t2::mac_message`** — never modified in this phase.
* **`class` is not ordered** — do not propose a privilege predicate over it.
* **The floor is project-specific** — `src/**`, `backend/**`, `services/**`, `app/**`, `packages/**` are all
  legitimate. `floor_requires_product=false` must stay false.

## 8. Lessons that cost this orchestration real time — they apply to you

* **Anti-stall.** A 420-minute stall came from a coordinator handshake with no timeout. A ~10-hour loss came from
  `pgrep -f <pattern>` inside a shell whose own command line contained that pattern — it can never exit. Every wait
  needs a bounded iteration count and a deterministic timeout action; prefer waiting on **file content**; if you
  match processes, prove the waiter cannot match itself. Never report liveness from a stale observation.
* **Test execution.** Never `--test-threads=1` (standing owner rule). Never pipe a test command without
  `set -o pipefail` — a red suite once reported exit 0 through `tail`. Never run bare `cargo fmt`.
  `. "$HOME/.cargo/env"` is refused by the worktree guard; use `"$HOME/.cargo/bin/cargo"` directly. The full suite
  costs ~60 min at ~373 tests on an idle machine, longer under load; load affects *timing*, never verdicts.
* **Evidence classes never collapse into "tests passed":** `BUILDER_REGRESSION`,
  `BUILDER_DEVELOPMENT_EVIDENCE`, `INDEPENDENT_ADVERSARIAL`, `HELD_OUT_ACCEPTANCE`. **A generative test is not
  independent merely because it generates many cases** — one round's test was named `..._for_any_class_value_...`
  and quantified over exactly the two values its author had implemented.
* **The most valuable thing a builder has produced here** is an accurate list of *the cases its generators cannot
  reach*, and one builder's declared deviation from its brief. Hold that standard in reverse: an unfounded green
  ships a defect, a manufactured objection costs a phase. Only the evidence is acceptable.

## 9. Current implementation state — **PENDING P2-AR-0096**

*(Filled in from the builder's report and the orchestrator's own verification before dispatch.)*

## 10. What you are entitled to assume, and what you must derive yourself

**Assume** (each independently established, and re-verifiable): the profile in §2; the trust statuses in §5; that
Level 1 and Property A are settled per §7; that the owner decisions in §4 are normative.

**Derive yourself**, without reference to any predecessor's framing: the attack domain; the generator domain; both
negative and positive controls; whether each previous finding is *genuinely* closed rather than narrowed; and whether
any mechanism introduced by the current round is itself defective — which is what happened in every one of the last
four rounds.

**A guard that refuses everything passes every negative test.** Build positive controls.
