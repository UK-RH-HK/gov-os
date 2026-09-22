# P2-HO-0055 — independent adversarial/property review of the A+C structural remediation

| Field | Value |
|---|---|
| Authorised by | **OD-P2-07** §7, the owner's architecture decision |
| Target | `phase2/remediation-ac` `35461c9` (P2-AR-0078), frozen |
| Execution | native Claude subagent, `claude-opus-5`, worktree-isolated |
| Evidence class | **`INDEPENDENT_ADVERSARIAL`** |
| Independence required | did not implement the change, did not participate in the builder session, did not author the builder's tests |

## What decides Phase 2 here

The owner's hard stop, verbatim:

> If the fresh Opus adversarial review finds another materially new HIGH blocker on the same: install-trust
> architecture; raw-command authority boundary; authority-enumeration pattern; project-editable exemption semantics —
> STOP again and return to the owner. … If the reviewer leaves a known HIGH materially open, also STOP.

If that happens, the escalation is toward **Option B** (constrain effects by isolation instead of predicting them) or
another owner-approved architecture review — **never another local repair round**. If the surface is sound, the
candidate is minted and formal acceptance verification follows.

## The two properties under review

**Property A.** *An installation reaches the ungated path only if every file it executes is pinned in the descriptor and
byte-verified immediately before execution. Anything not reducible to an exact bound artefact is `undetermined` and
gates.*

**Property C.** *Project-editable classification state cannot silently increase effective authority or obtain a
governance exemption.*

**Derive the attack domain yourself from these properties.** Do not take the builder's test generators as the definition
of completeness — that failure is precisely why this round exists (P2-AR-0077 found a test named *"for any class value"*
quantifying over the two values its own author implemented, against a real vocabulary of six).

## Priority targets — the builder named its own gaps, so start there

P2-AR-0078 declared these unprompted. Self-declared gaps are where defects live.

1. **The `UnrecognisedProgram` decoupling.** The builder's own words: *"a fresh reviewer attacking specifically the
   decoupling decision rather than the list-shrink is the most likely place I'd be wrong."* A new `Unreadable` enum
   splits `Opaque` from `UnrecognisedProgram`; the latter still runs the per-token privilege/host/credential/path/network
   scan even though the command gates. The builder reasoned this can only *add* findings, never lift the gate, but never
   constructed adversarial argv designed to make the **decoupled scan itself** misbehave — e.g. a token reaching
   `resolves_outside_project` or `endpoint_host` by this new path that panics, or that produces a finding which some
   later consumer treats as authorising. **Verify the "can only add findings" claim by execution, not by reading.**
2. **The surviving `plain_argument_programs: ["true","false"]`.** The justification is that both are POSIX-defined to
   ignore every argument with zero effect — a structural property, not a smaller enumeration. Attack it: is there *any*
   argv under which a shell resolves `true`/`false` to something else (a project-local `./true`, `PATH` shadowing, a
   builtin-versus-binary difference, an alias)? Note the mild circularity that the builder also swapped tests to use
   `true` as an inert vehicle. **If this residual is sound, say so plainly — a two-entry list with a provable property
   is not the same defect as a six-entry list with a false premise.**
3. **`argument_indirection_flags` survived**, on the argument that it still gates a pinned script's *trailing arguments*
   (`sh install.sh -K`). Since argv is bound by `review_subject`, is this mechanism load-bearing, redundant, or a
   residual enumeration? Either answer is useful; an enumeration kept for no reason is a finding.
4. **AR77-F1, F2 and F4 are closed *by construction*, not fixed.** `endpoint_host`'s empty-authority `file://` bug and
   the hard-link blindness are **still in the code**, unreachable only because `curl`/`cp` left the list. **Find another
   route to those code paths.** Any program still reaching the per-token scan, any other caller of `endpoint_host` or
   `resolves_outside_project`, `health_one`'s lifetime path, `uninstall_command` — if a route exists, the finding is
   alive and this is the highest-value attack in the brief.
5. **Property C's exemption vocabulary.** The `Exemption` enum has **two** variants. Is that the complete set of *kinds*
   of exemption? Check `SECRET_CLASS`, the `"historical"` branches, `derived_deletion_set` (deliberately not migrated),
   and `lineage.rs`'s `CODE_CLASSES`/W7/W11 — the builder judged the last **descriptive** and flagged it as a judgement
   call. **If escaping an audit sweep is itself a governance exemption, that judgement is wrong and it is a HIGH.**
6. **Future-consumer divergence.** The builder concedes nothing mechanically prevents a new consumer writing its own
   `matches!` again — only doc comments. Is that acceptable, or does the property fail the moment someone does?

## Then the surface proper

7. **Does the ungated path still exist at all?** Property A must not become "gate everything". Independently verify a
   **conforming pinned-artefact install proceeds ungated with zero gate records**, that `gov init` on brownfield refuses
   nothing, that legitimate governed declarations are honoured, and that a governed change may still classify paths as
   evidence/generated/derived. OD-P2-03 requirement 6 is violated by over-gating exactly as requirement 3 is by
   under-gating.
8. **Does `review_subject` really bind argv?** The builder verified this operationally and it is load-bearing for the
   whole architecture — a pinned script with attacker-chosen arguments is a different installation. Re-derive it.
9. **Re-test AR77-F1/F2/F3/F4 independently**, and enough of the previously-closed install-trust attacks (AR68-F1..F6,
   AR73-F1..F6, AR75-F1/F2) to establish the structural change did not reopen them.
10. **The changed test assertions.** Six tests had bodies changed under a pre-authorisation, no renames. Verify each new
    assertion is genuinely **stricter** and that none was weakened to pass.

## Method

Write your own probes and property generators. Prove effects by **actual filesystem and governance outcomes** — a file
appearing outside the root, a task closing that should have been refused — never by reading a status field. Use
disposable projects each with its own `XDG_STATE_HOME`. **Delete nothing**: move aside, as previous reviewers did.

Preserve your probes as independent evidence and commit them. **Do not modify product source.**

## Regression evidence already established — do not reproduce it

The orchestrator ran the full certification suite independently on this exact commit, machine-exclusive at default
`--test-threads` from a verified-idle machine (load 0.99, zero competing processes). **Those figures are recorded in
`AGENT_RUNS/P2-AR-0078.run.yaml` and you do not need to re-run the suite** — it costs ~50 minutes. Reproduce it only if
you have a specific reason to doubt it, and tell the orchestrator first.

Targeted runs are cheap. `. "$HOME/.cargo/env"` first; never pipe a test command without `set -o pipefail`; never pass
`--test-threads=1`; never run bare `cargo fmt`.

## Stall protection

`worker_stall_protection` is ACTIVE. **Never wait on the coordinator indefinitely.** Evaluate machine preconditions
yourself and proceed automatically when satisfied. If you genuinely need a decision, report `BLOCKED_ON_COORDINATOR`
with why, what you await, a **timeout** and the **default action** you will take — then take it.

## Deliverable

Verdict — exactly one of `SURFACE_SOUND` · `RESIDUAL_DEFECTS` · `INCOMPLETE` — then:

- **Property A and Property C each**: holds or fails, and **how you proved it** by your own reproduction.
- **Findings**: id, severity, class, **residual or materially new** (this decides whether the owner is called), and a
  concrete reproduction with observed effect.
- **Negative controls**, each with observed result, establishing the surface does not pass by gating everything.
- **The prior findings** you retested, each confirmed closed or not.
- **Your verdict on the builder's four judgement calls**: the `["true","false"]` residual, `argument_indirection_flags`
  surviving, `derived_deletion_set` staying separate, and `lineage.rs` being descriptive.
- **What you could not probe**, named.
- **Your commit SHA.**

Say plainly if you think the architecture is sound. Four rounds have been defeated on this surface and a fifth failure
escalates to a deeper architecture — but a false alarm also has consequences, stopping Phase 2 and calling the owner for
nothing. Distinguish clearly between what you proved, what you suspect, and what you merely could not rule out.
