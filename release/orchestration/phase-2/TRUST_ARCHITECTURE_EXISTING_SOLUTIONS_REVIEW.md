# Trust architecture — existing-solutions review

| Field | Value |
|---|---|
| Date | 2026-09-23 |
| For | the product owner |
| From | the Phase-2 outer orchestrator |
| Authorised by | the owner's read-only architecture research authorisation, 2026-09-23 |
| Status | **Research complete. Nothing implemented. Phase 2 remains STOPPED.** |
| Depth | 6 researchers (Sonnet 5) → 1 synthesis (Opus 5) → 1 independent challenge (Opus 5) → 1 amended synthesis. ~5,900 lines of evidence under `RESEARCH/`. |
| Read next, in order | `RESEARCH/SYNTHESIS.md` (rev 2, 1,199 lines) · `RESEARCH/SYNTHESIS-CHALLENGE.md` (547) · `RESEARCH/ORCHESTRATOR-MEASURED-ENVIRONMENT.md` (322) |

---

## 1. Executive summary

**Two things you were told are wrong. Both were found by measurement, and both were reproduced independently by me.**

1. **The Property-A fix I recommended to you would not have worked.** The Option B escalation package said clearing the
   environment, pinning the working directory and executing by resolved absolute path would close both open HIGHs.
   **Two of those three limbs do nothing.** `env` is not an environment variable — it is a *program*, and `PATH=.` and
   `--chdir=` are arguments it applies inside the child after `gov` has lost control.
2. **The Property-C prerequisite I told you to settle first does not exist.** P79-F10 reported that the product has no
   way to distinguish a governed change from a hand edit. **`runtime/src/cit/binding.rs` already implements exactly
   that**, T2-sealed and bound to an owner-signed Human Decision Gate, and the primitive is general
   (`SEALED_RECORD_TYPES = ["human-gate","cit","task"]` — the path map is simply not a member).

**Then the study did it to itself.** The synthesis's own replacement fix was defeated the same way, by execution: a
hash-pinned artefact whose shebang reads `#!./w` runs an unpinned project file — and the control shows the attack
*requires the working directory the OS itself pins*. The mitigation supplies the attacker's resolution root.

**The recurring defect has a name and a 1988 citation**: the **confused deputy** problem (Hardy), with Miller's *No
Ambient Authority* as its precise formal statement. We have been rediscovering it in a private vocabulary for five
rounds.

**The recommendation is Option 1: four changes, no new dependency, net reduction in trusted code.** It closes all four
open HIGHs (P79-F1, F8, F9, F11 — F8/F9 conditional on precondition **P1** below), deletes more than it adds, and is
reversible at the code level.

**What we would avoid building**: a bidirectional exemption predicate (impossible — `class` is a label, not a level); a
"detect a hand edit" mechanism (the wrong verb; authenticate the transition instead); a sandbox for Phase 2 (closes no
open HIGH); and a replacement for the accepted Level-1 release root (would reopen the frozen RoT-1 dispute).

---

## 2. The core trust problem, R0 → R1 → Phase 2

One shape, five recurrences:

```
lower-trust input → representation → Governance OS interprets it → higher-trust authority or execution effect
```

> **The check reasons about a representation; the authority or effect is determined somewhere the representation does
> not cover.**

| Round | Mechanism | Defeated by |
|---|---|---|
| 1 | per-token argv scan | wrapping |
| 2 | positive allowlist of readable shapes | 25 shapes |
| 3 | inverting the fail-open default | the inversion **held**; two list entries' premises were false |
| 4 | fixing those entries | the same program, twice more; `class` compared 2 of 6 values, 1 of 2 consumers |
| 5 | one authoritative predicate | the predicate models exemptions **granted**, not obligations **lost** |

**The canonical name**: confused deputy (Hardy 1988, ACM SIGOPS OSR 22(4)); Saltzer & Schroeder 1975 *complete
mediation*; Miller 2006 *No Designation Without Authority* / *No Ambient Authority*. A contemporary treatment of
precisely the LLM-agent shape exists (Santos-Grueiro, arXiv:2607.06000) and names our Property-C failure *"authority
laundering"* — **but its peer-review status is unconfirmed and it is weighted as a design sketch, not settled
literature.**

---

## 3. Level 1 landscape — trusting Governance OS itself

Governance OS already implements a TUF-shaped role model by hand: root/release/snapshot/timestamp roles, Ed25519
threshold signatures (strict-only; the permissive fallback was deliberately removed), root rotation matching TUF's
co-signing protocol, and durable monotonic high-water marks — the correct offline substitute for TUF's online
timestamp freshness. It already avoids one classic trap by signing raw `RawValue` bytes rather than reimplementing JCS
canonicalisation.

**The strongest "stop building" observation, and why I am not acting on it**: the R1 builder evaluated AWS Labs'
`tough` (maintained Rust TUF client, offline-capable) and declined it because its generic `custom` field would hide
typed bindings. Agent 1 assessed that as justifying *not using it for the whole model* rather than *hand-writing all of
it*, and noted the seven rejected RoT-1 revisions' HIGH findings map almost bullet-for-bullet onto TUF's own attack
taxonomy — evidence of rediscovering known attacks.

**Excluded from every recommendation here**: the RoT-1 lineage is **rejected in all seven revisions and frozen pending
your meta-architecture review**; `D-0008` and `ARCH-0002` are `PROPOSED`, not active. Touching Level 1 would reopen it.

**Sigstore does not fit**: keyless requires an OIDC provider, Fulcio and Rekor, and its own trust root is distributed
*via TUF* — reinforcing TUF as the right foundation. **crates.io has no production package signing** — a real,
unclosable supply-chain gap for a Rust project that no library choice fixes.

---

## 4. Level 2 landscape — decisions, state and execution

**The finding that reframes it**, from the product's own source (`runtime/src/tools.rs`):

> The token and pattern lists are **a kernel floor, never a safety proof**: the OS **cannot confine a spawned
> process**, so what it cannot observe is carried by the independent governed security review.

The architecture has always known this. Five rounds tried to *observe* more.

**2A/2C — governed state.** Five independent traditions converge on the same move: stop asking *"does this look like a
legitimate edit?"*, ask *"did these bytes arrive through a channel only an authorised principal can produce?"* — TUF,
OPA signed bundles, SELinux's compile-then-load boundary, in-toto/SLSA provenance, object-capability theory.

**2B — execution.** `execveat(2)`/`O_PATH` (measured working here for binaries *and* `#!` scripts), Bazel's
`--incompatible_strict_action_env` (shipped default since 0.21), Nix's absolute-path pinning through a cleared
environment.

---

## 5. Level 3 landscape — isolation

Landlock is the only candidate proportionate to this deployment. **Measured on this machine**: ABI 3, default-enabled
LSM, full `create_ruleset → add_rule → restrict_self` cycle **with no root**, real `EACCES` enforcement.

**A trap found by probing, not reading**: `LANDLOCK_ACCESS_FS_WRITE_FILE` governs opening an *existing* file for write
and **does not cover creating a new one** (`MAKE_REG` and siblings). A ruleset handling only `WRITE_FILE`/`READ_FILE`
leaves file creation unrestricted **everywhere, silently**.

Everything else — containers, gVisor, Firecracker, WASI, remote execution — is oversized for one owner on one machine.
`/dev/kvm` exists but the user is not in the `kvm` group; Docker is a root-owned daemon; rootless prerequisites are
partial.

**Held to the standard Agent 4 set for itself: Landlock would not have stopped P79-F11** (`decoy/` is inside the
allowed subtree) and contributes **nothing** to Property C.

---

## 6. Technologies considered

Full per-candidate records — security property provided, property **not** provided, trust assumptions, maturity,
licence, offline/WSL2 fit, root requirement, TCB delta — are in the six `RESEARCH/AGENT-*.md` files. Summary of
dispositions:

| Technology | Disposition |
|---|---|
| `execveat`/`O_PATH`, `env_clear`, constructed `envp` | **USE DIRECTLY** — kernel + std, measured here |
| `t2::seal_*`, `cit::binding`, `human_channel` Ed25519 | **USE DIRECTLY** — already in the product |
| git content-addressed objects | **USE DIRECTLY** — already a dependency |
| Bazel strict-action-env; SELinux `neverallow`; OPA multi-bundle AND-composition | **ADAPT THE PATTERN** |
| Landlock (`landlock` crate) | **WRAP** — R2 |
| `tough` (TUF client) | **WRAP** — but Level 1, excluded (frozen dispute) |
| bubblewrap / namespaces | **WRAP** — R3 |
| Nix, Guix, Bazel, Buck2, Pants, OCI runtimes, Flux, Argo CD, gVisor, Firecracker, WASI | **not adopted** — pattern only |
| Sigstore keyless, Uptane, TPM sealing, K8s admission | **excluded** — require infrastructure we do not have |

---

## 7. Requirement-to-solution matrix

| Requirement | Status |
|---|---|
| first-install authenticity · update authenticity · rollback protection | **EXISTING SOLUTION** (SRR-1, accepted; TUF-shaped) |
| exact-byte binding · review-to-artefact binding | **PARTIALLY SOLVED** — `pinned_files` exists; §12 gap |
| **verified-byte → executed-byte binding** | **EXISTING SOLUTION** — `execveat`/`O_PATH` + shebang closure |
| **environment-mediated execution rebinding** | **EXISTING SOLUTION** — reduce the wrapper chain, do not execute it |
| **cwd-mediated rebinding** | **EXISTING SOLUTION** — same reduction (note: cwd *pinning alone made it worse*) |
| PATH/interpreter/loader substitution | **PARTIALLY SOLVED** — probe **P2** outstanding |
| **project configuration self-authority** | **EXISTING SOLUTION, IN-REPO** — floor composition + T2 seal |
| **hand edit vs governed transition** | **EXISTING SOLUTION, IN-REPO** — `cit::binding` pattern |
| authority increase · obligation removal · policy precedence | **EXISTING SOLUTION** — floor from authenticated kernel content |
| effect containment · command-side mutation | **EXISTING SOLUTION** — Landlock (R2) |
| tool/plugin acquisition | **GOVERNANCE-OS-SPECIFIC** — the one `BUILD CUSTOM` |
| multi-project separation · offline operation | **EXISTING / SATISFIED** |
| local-machine trust assumptions | **NOT DETERMINED** — see §15 |

---

## 8. Defect-by-defect

| Defect | Option 1 closes? | Evidence |
|---|---|---|
| **P79-F11** verified ≠ executed | **YES** | reduction + shebang closure; measured |
| **P79-F1** env rebinding | **YES** | wrapper ⇒ `undetermined`; measured |
| **P79-F12** health-check recurrence | **YES** | same path |
| **P79-F8 / F9** obligation removal | **YES for kernel-layout projects; NO for `gov adopt` native layouts** — precondition **P1** |
| AR68/AR73 command-shape family (~40) | **YES** — structurally irrelevant once the object is executed |
| AR77-F1/F2/F4 (effects) | **NO** — needs Landlock (Option 2) |
| R0/R1 unauthenticated source | **NO** — Level 1, out of scope |
| **Landlock alone** | closes **no open HIGH's underlying defect** |

---

## 9. USE DIRECTLY / WRAP / ADAPT / BUILD CUSTOM

**One `BUILD CUSTOM` survives the whole study**: the `ResolvedExecution` reduction — roughly 40 lines inside an
existing function, plus the shebang closure. Everything else is USE DIRECTLY (kernel syscalls, std, in-repo
primitives), ADAPT (Bazel/SELinux/OPA patterns), or WRAP-deferred (Landlock at R2).

---

## 10. Simplification opportunities — quantified

| Deleted | Count |
|---|---|
| `installation_envelope` entries encoding exec semantics | **45 of 106** (the other 61 answer a different question and stay) |
| `LOADER_ENV_VARS` denylist | **30 entries** — and it does **not** contain `PATH`, `IFS` or `GIT_SSH_COMMAND` |
| `skip_wrappers` / `wrapper_programs` | entire mechanism; no replacement needed — the inverted default already gates |
| comparison machinery | **≈250 of ≈447 lines** (reporting retained for OC-P2-04 §4) |

**And two unfalsifiable obligations become decidable propositions**:

- OD-P2-07 C demanded "search for ALL consumers" of `class`. `PathDecision` — the only type with `.class()` — is
  constructed at **exactly one site** (`paths.rs:710`). Discharged **by type construction**, not by search.
- Property A's guarantee becomes falsifiable by **two** tests ("is the exec'd fd the hashed fd?", "is every program the
  kernel resolves before the first reviewed instruction in the hashed closure?") instead of an unbounded enumeration.

---

## 11. Local/private profile · 12. R2 · 13. R3

**Now (Option 1)**: the four changes. No new dependency. **R2 (Option 2)**: Landlock for the effects residual;
`memfd_create` sealing for staged content; schema-constrain `pinned_files`; in-toto Statement shape for evidence
digests. **R3 (Option 3)**: bubblewrap → rootless containers → gVisor/microVM, only if the profile becomes
multi-tenant. Option 1 forecloses none of it.

---

## 14. Recommended architecture — Problem A (execution trust)

> **The OS executes a kernel object it holds, never a name it was handed — and nothing inside that object may name a
> second one.**

The clause after the dash is the amendment the challenger forced. Five obligations (`SYNTHESIS.md` §9.2), of which the
second is new: read the artefact's first line; fail to `undetermined` unless there is no `#!`, or the `#!` names an
**absolute** interpreter the OS resolves, opens and hashes **inside the same `ResolvedExecution`**, and which is not
itself a re-exec vector. Relative, `env`-fronted and `-S`-carrying shebangs are reduction failures.

---

## 15. Recommended architecture — Problem C (governed authority-bearing state)

**Floor composition, not comparison.** The current predicate diffs one mutable file against a reference snapshot of
*itself* — the only content-comparison approach in the entire study. Every mature system's precedence is *structural*.
Take `class` from the kernel rules wherever a kernel rule matches; the floor comes from `trust.policy_root`, which is
**authenticated kernel content** — which is why it needs no key and is *stronger* than the seal.

**Add `"repository-contract"` to `SEALED_RECORD_TYPES`** for detection, plus an owner-gated route for legitimate
widening.

**The caveat you must carry** (§18): the T2 seal is HMAC-SHA256 under a **symmetric** key readable by any process with
your OS privileges. The module's own words: *"detection-grade, not proof"* — and the sentence the synthesis initially
truncated adds that a forgery is **honoured on your other provisioned machines**, with revocation per key, not per
machine. The lower-trust party here *is* an AI agent on your account. **Floor composition needs no key; `human_channel`
binds to an Ed25519 key `gov` does not hold.** Those two are the proof-grade anchors; the seal is defence in depth.

---

## 16. What could be deleted

See §10. Net TCB reduction: the classifier's semantic model of shells and interpreters goes; two syscalls in an
already-trusted kernel arrive.

---

## 17. Migration implications

No data migration, no format change, no external dependency to unwind, no schema change. **One qualification neither
the synthesis nor the challenger verified**: deleting `wrapper_programs` changes the kernel payload, hence
`KERNEL_MANIFEST.json`, `framework.lock`, the embedded payload and this machine's SRR installation record, plus an
`ENFORCEMENT_MAP.yaml` edit. *"Reversible in an afternoon"* is right about the code and is **an unverified claim about
the release transaction**.

---

## 18. New dependencies and their risks

**Option 1's minimum: none.** The descriptor-exec increment adds `nix` (MIT, maintained). Option 2 adds `landlock`.
Option 3 adds an external binary plus a bespoke security-critical flag policy — the largest TCB addition of the three.

---

## 19. Open questions requiring your decision

1. **P1 — precondition, not a question.** `adopt.rs:1579/1585` generates **unfloored** rules for non-`product/`
   layouts, so floor composition closes **zero** of P79-F8/F9 for `gov adopt` projects. Does the floor extend past the
   kernel template's coverage? And per OC-P2-04 §4, *"this path is unfloored"* must be **observable**.
2. **The corrected Property-A fix is not authorised.** "Do not execute wrapper chains" is a behaviour change for
   installers legitimately using `env`/`nohup`/`timeout`.
3. **Is detection-grade acceptable** for the path-map seal, given §15?
4. **What does the governed route for a class change cost** in your workflow?
5. **Landlock at R2, or never?**
6. **Re-scoping to R2** — note the two corrections move that arithmetic in *opposite* directions.
7. **The `pinned_files` schema gap** (§12 of `SYNTHESIS.md`): the field carrying the entire bind-the-bytes guarantee
   appears 7 times in `tools.rs` and **0 times in the schema**, which sets no `additionalProperties`.

**And one obligation, not a question: probe P2 must run before implementation** — a pinned, dynamically-linked ELF with
project-controlled `RUNPATH`/`$ORIGIN`/`LD_*`. `LOADER_ENV_VARS` is stripped on the plugin path only, **not** at
`run_cmd`. Three lines of test. This pattern's record in this study is five for five.

---

## 20. Sources

Per-candidate citations are inline in the six agent reports: TUF, in-toto and SLSA specifications; OPA, Nix, Bazel,
bubblewrap, gVisor, Firecracker and WASI documentation; kernel documentation and man7 for `execveat`, Landlock and
namespaces; rust-lang/rust source (not merely docs) for `Command`'s environment handling; Hardy 1988, Saltzer &
Schroeder 1975, Miller 2006, Chen/Wagner/Dean 2002, Cahill et al. SIGMOD 2008. **Four 2024–2026 arXiv papers are
flagged as peer-review-unconfirmed and weighted as design sketches.**

---

## 21. Independent synthesis-review findings

The challenger's verdict: **fit for the owner after one substantive amendment**, which has been made. It achieved the
outcome the brief valued most — a concrete defeat by execution — and it **agreed explicitly** where it agreed: level
separation is clean, the dependency declines are right (including declining bubblewrap immediately after a measurement
made it *easier*), `class`-is-a-label is verified in code, Landlock-at-R2 is adjudication rather than overruling, and
refusing to reopen RoT-1 is correct.

It also *strengthened* two claims beyond what was argued, and corrected counting errors in both directions — including
one where the synthesis had counted a declaration's **lines** rather than its **entries**: the study's own error, in
the document arguing against it.

---

## 22. Recommendation

**Option 1 — resolve once, execute the object; floor the class.** Four changes, no new dependency for the minimum, net
reduction in trusted code, reversible at the code level, and it closes every open HIGH subject to **P1**.

**Option 2 (Option 1 + Landlock) is its correct R2 successor** — not now: it closes no open HIGH and introduces a
Level-3 mechanism while HIGHs are open.

**Option 3 (full hermetic execution) is a genuine architecture whose time is not now** — and decisively, **it needs
Option 1 inside it regardless**, because `./w` is a declared input, so both proven defeats survive inside a bubblewrap
jail unchanged.

**The strongest evidence behind this**: every load-bearing claim was measured on this machine, not argued — and the
method repeatedly falsified its own authors, including me twice. The two remaining qualifications are stated rather
than buried: **P1**, and **probe P2 has not been run**.

**Nothing is implemented. Phase 2 remains stopped, awaiting your decision.**
