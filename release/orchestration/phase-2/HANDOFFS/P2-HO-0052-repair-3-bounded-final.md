# P2-HO-0052 — Repair round 3 (bounded, final): AR75-F1, AR75-F2, AR75-F3

| Field | Value |
|---|---|
| Authorised by | the product owner, 2026-09-22, choosing **Option A** from `PHASE_2_PRE_MINT_DECISION_PACKAGE.md` |
| Scope | **exactly** AR75-F1 and AR75-F2, plus AR75-F3's incorrect justification. Nothing else. |
| Base | `phase2/repair-2-failclosed` `c34c439`, `product_code_digest b6f75daf…2929` |
| Execution | native Claude subagent, `claude-sonnet-5`, worktree-isolated |
| Follows | P2-HO-0051 (repair-2 common protocol) in full, with the amendments below |
| Next | one fresh Opus 5 adversarial review; then mint `cap2-candidate-2` **only** if it finds no blocking defect |

## Why this round exists, and why it is the last one on this surface

P2-ADJ-0006 committed the orchestrator to stopping after one structural round rather than iterating a fourth time. The
round landed: the classifier's fail-open default **was** inverted, and P2-AR-0075 confirmed the inversion holds — an
arbitrary unnamed program gates, unnamed wrappers gate, and a project cannot touch the policy lists. The orchestrator
therefore stopped and escalated, as promised, and the owner has authorised one bounded round for the two HIGH defects
that remain.

The owner's authorisation is narrow and its boundaries are binding:

> Authorise Option A: one final bounded repair round for exactly AR75-F1 and AR75-F2. Do not mint `cap2-candidate-2`
> while either HIGH finding remains open.

And the owner's stop condition, which the orchestrator will honour:

> STOP and return to me for an architecture/meta-review if that fourth adversarial review finds another materially new
> HIGH blocker on the install-trust surface; or leaves AR75-F1 or AR75-F2 materially open.

## AR75-F1 — the demonstrated `cp`/`curl` escape (HIGH, BC-P2-53)

**What is true today.** `framework/policies/TOOL_POLICY.yaml:114` lists
`plain_argument_programs: ["true", "false", cp, curl, sudo, apt-get]`. The premise of that list, stated in
`runtime/src/tools.rs:1175`, is that these are programs "the OS can read completely, because none of its own arguments
carry code, wrapping or file-execution meaning". For `cp` and `curl` that premise is **false**: `cp` writes *through* a
destination symlink, and `curl -K <file>` reads the rest of its command line from that file.

That alone would be latent. What makes it exploitable is `runtime/src/tools.rs:1527`:

```rust
if !c.contains('/') && !c.starts_with('~') {
    continue; // not a path the OS can read as one
}
```

A token with no slash is never evaluated as a path at all, and `leaves_project` (`tools.rs:1292`) is purely **lexical** —
absolute, `~`, drive-qualified, or a `..` segment. Neither sees a symlink. P2-AR-0075 demonstrated six shapes that install
`not_gated`, with `expands_authority false`, no triggers, nothing `undetermined`, **zero gate records**, and a marker
written in the parent of the project root. Five contain no slash, no `..` and no absolute path anywhere in argv. Two sit
in `health_check.command` and re-fire on every later `gov tools health`.

**The owner's instruction, verbatim:**

> close the demonstrated cp/curl command-shape escape without returning to an interpreter/program denylist. Follow the
> reviewer's principled fix: evaluate every relevant non-flag argument relative to the project boundary rather than only
> tokens containing a slash, and make the proof sensitive to actual escape behaviour including symlink-resolved
> destinations. Preserve ordinary conforming acquisition and all existing negative controls.

**Why boundary resolution is the right shape, and why it is not enumeration.** Resolving a token against the project root
does not require knowing whether the token *is* a path. A bare word like `install` or `--version` resolves to
`<root>/install`, which does not escape, so it is inert. Only a token that genuinely resolves outside the root — including
through a symlink — is reported. The OS therefore stops guessing which tokens are paths and instead answers the only
question that matters: *could this token name something outside the project?* Removing the slash precondition makes the
check strictly more cautious, which is the direction OD-P2-05 clause 3 requires.

**Design notes, not a design.** Satisfy the requirement; if a better mechanism exists, say so and why.

- A destination that does not exist yet cannot be canonicalised. Resolve the deepest existing ancestor and judge the
  remainder lexically against it. A component that cannot be resolved at all is `undetermined`, not "fine" — fail
  towards the gate (OD-P2-05 clause 3).
- Symlink resolution must not be confined to the final component: an intermediate symlinked directory escapes just as
  effectively, and P2-AR-0075 noted AR73-F6's canonicalisation already covers a symlinked *parent*.
- Resolution reads the filesystem, so it is inherently TOCTOU-prone. That is already disclosed residual risk for this
  surface; do not try to solve it here, but do not let a resolution *failure* read as "no escape".
- **`curl -K` is a different mechanism from `cp`, and boundary resolution alone does not close it**: the config file is
  itself inside the project, and the escape happens because `curl` acquires arguments the OS never saw. Close it by the
  least-enumerating sound means you can justify from the sources, and state plainly in your result which you chose and
  what it costs. Note that `TOOL_POLICY` already has a general mechanism for "a flag meaning the rest is more program,
  not an argument" (`inline_code_flags`, `is_inline_code_flag`) and that OD-P2-05 clause 2 covers code with no artefact
  to pin. Note also that the only certification dependency on `curl` being *listed* is the shape
  `["curl", "-sS", "<https url>"]` (`r2_wsa.rs:433`, `r4_residual.rs:1212`, `:1299`, `:1319`) — no test requires `curl`
  to accept a **file** operand.
- If you conclude the only sound options force a genuine trade-off between OD-P2-03 requirement 6 (a conforming
  installation proceeds ungated) and OD-P2-05 clause 3 (fail closed), **implement the fail-closed one**, record the
  usability cost explicitly, and flag it as `OWNER_DECISION_REQUIRED` in your result *in addition to* landing the fix.
  Fail-closed is the standing rule; the owner decides whether to pay its price, and cannot do so without your measurement.

**Forbidden.** A denylist of programs or a per-program table of argument semantics. That is the method that has now
failed three times, and the owner has ruled it out by name.

## AR75-F2 — `class` is authority-bearing and is not compared (HIGH, BC-P2-45 / OC-P2-04)

**What is true today.** `overlap_is_no_less_restrictive` (`runtime/src/policy_precedence.rs:565`) compares `mutation`,
`agent_read`, `export`, `sensitivity` and every index/retrieval flag, and its doc comment says — correctly — that it
compares them "as `rule_effective_attrs` actually decides them, not as raw YAML fields". It then *deliberately* does not
compare `class`, for a reason that is also correct as far as it goes: a genuinely new, more specific pattern legitimately
carries a different label (`tests/certification/repair.rs::sensitivity_classes_and_namespaces_are_enforced` classifies
`product/legal/**` `authoritative` against the kernel's `product/**` `source`).

**What it missed is a consumer.** `runtime/src/orchestration/tasks.rs:947`:

```rust
fn contract_generated(p: &Project, path: &str) -> bool {
    let d = p.contract().decide(path);
    matches!(d.class().as_str(), "generated" | "derived")
}
```

`class` therefore decides **whether a mutation is observed at all**. P2-AR-0075 appended
`{pattern: "product/*.yaml", class: derived}` — equal or stricter on every compared dimension — and turned a refused
`MUTATION_SCOPE_VIOLATION` into an accepted close: observed mutations went from one to none, and `policy overrides`,
`D027`, the `policy_precedence` family and `path_map_compliance` all stayed clean. `globprobe` confirmed the check **saw**
the overlap and passed the rule, so this is not a pattern miss.

**The owner's instruction, verbatim:**

> treat `class` as authority-bearing in restrictiveness/overlay comparison because `class: derived` changes whether
> mutations are governed/observed. A project-side declaration must not gain an exemption merely by changing class.

**The function's own philosophy already tells you the shape.** Do not compare class *labels*; compare what class
**decides**. The observation exemption `generated`/`derived` confers is an effective dimension exactly like `mutation` or
`export`, and it belongs in the same loop. A candidate that makes an observed path unobserved is widening authority; a
candidate that is `authoritative` where the kernel says `source` is not, and must keep working. Both halves are testable,
and the second is a required negative control.

Apply the fix at **both** call sites — `evaluate_path_rules` (`:668`) and `evaluate_path_rules_overlay` (`:807`), the
production path — and check whether `path_rule_narrowing` needs the same treatment for an in-place edit.

## AR75-F3 — a factually wrong justification (LOW, correct the reasoning only)

The comment at `policy_precedence.rs:~567–585` excludes `mutation` from comparison for a `class: secret` candidate, and
justifies it by asserting that `decide()`'s `secret_locked` latch "never touches `mutation` … and leaves `mutation` to
whichever OTHER rule actually governs a given concrete path". **P2-AR-0075 measured that this is wrong**: `decide` applies
a later secret rule in full, so the appended rule's own `mutation` wins. An attacker may claim `class: secret` freely, and
it does widen mutation — `archive` restricted→allowed, `governance/kernel` prohibited→allowed — with nothing reported.

It is LOW because it is **not exploitable today**, for reasons the reviewer measured and which must be stated accurately
if they are to be relied on: the only consumer of `decide().mutation` here is pre-empted by the secret-sensitivity branch
above it (the install still gates, on a different trigger), the two prohibited checks read the raw rules array, declaring
`secret` costs the attacker every other dimension, and an explicit `export` override on the same rule is still refused.

**The owner's instruction, verbatim:**

> Also correct AR75-F3's factually incorrect justification while touching this surface, but do not turn that LOW item
> into broader architecture work.

So: make the comment true. If the exclusion can be narrowed or removed without breaking the AR73-F3 fallout it was
written for (a single-segment `class: secret` adoption pattern overlapping restrictive kernel directories), do that and
say so. If it cannot, keep the exclusion but state the **real** reason it is inert, name it as a defence-in-depth gap
rather than a proof, and leave it for the formal verifier as disclosed residual risk. Do not redesign the latch, and do
not widen this into the `secret`-skip in the overlap scan — that is a separate, differently-justified exclusion.

A wrong comment on a security control is worse than no comment: it is what the next reader will rely on. That is the whole
reason this LOW item is in scope.

## Acceptance evidence this round must produce

P2-ADJ-0006 changed the standard, and it still applies: **the acceptance evidence for a classification repair is a
property over the default, not the previous reviewer's shape list.** Its exact words:

> The reviewer's shapes remain as **regression** guards only, never as the definition of done. A repair that adds a name
> to a list, without changing the default, is not a repair of this class.

Concretely:

1. A **property** test for AR75-F1 over *arbitrary* non-flag tokens: a token that resolves outside the project root is
   reported, whether or not it contains a slash, and whether it escapes lexically or through a symlink. Generate the
   shapes; do not enumerate the six.
2. A **property** test for AR75-F2: a candidate rule that removes a path from governed-mutation observation is refused,
   for any class value that confers the exemption, on any overlapped kernel rule.
3. The six AR75-F1 shapes and the `product/*.yaml` `class: derived` rule as **regression guards**.
4. **Negative controls that must still pass** — these are not optional, and a repair that breaks one is not a repair:
   `cp` with both operands inside the project installs ungated; `["curl","-sS","<https url>"]` behaves as its three
   existing tests require; a conforming install proceeds with **zero** gate records; `product/legal/**` `authoritative`
   against kernel `product/**` `source` is still honoured; a legitimate `generated` declaration on a tree the kernel
   already treats as generated is still honoured; `gov init` on a brownfield repository still succeeds and refuses
   nothing.

## Testing protocol for this round

The owner has directed targeted iteration and exactly one genuine full suite, because the full certification run
currently costs ~2.5 hours (a separate performance diagnostic is running in parallel and does not block you):

> use targeted tests while iterating; then affected dependency tests where appropriate; run only one genuine full
> certification suite once the repair is ready for adversarial review.

So: iterate on the affected certification binaries and the unit tests. When the repair is complete, run **one** full
certification suite and report its exact figures. Do not claim a figure you did not observe. Every check must run through
the `pipefail` wrapper — a suite piped through anything else can report exit 0 while red, which is a defect this
orchestration already had once and fixed.

## Scope boundaries

`allow_write`: `runtime/src/tools.rs`, `runtime/src/policy_precedence.rs`, `framework/policies/TOOL_POLICY.yaml`,
`tests/certification/r2_failclosed.rs`, and **one** new certification test file for the property tests, declared in
`tests/certification/main.rs` and added to `tests/governance/capability-evidence-map.yaml`.

Everything else is out of scope. In particular: **no test renames** (the evidence map names tests by exact path, and a
rename fails `gov contract verify`, the binding-chain test and `release build`); no weakening of any existing assertion;
no reach into `runtime/src/orchestration/tasks.rs` to change what `contract_generated` means — the defect is that the
*comparison* ignores it, not that the exemption is wrong.

If closing either finding requires a file outside that list, **stop that item and say so** rather than reaching for the
file. That is how AR68-F2 was handled correctly by P2-AR-0070, and the adjudication that followed (P2-ADJ-0004) exists
because the worker declined to force it.
