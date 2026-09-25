# P2-HO-0061 — Review 8: the convergence decision point (P2-AR-0097)

| Field | Value |
|---|---|
| Subject | **`3c880d8`**, branch `phase2/review-8` |
| Your role | **fresh independent adversarial reviewer.** Not the builder, not the orchestrator. No role grades its own work. |
| Evidence class | **`INDEPENDENT_ADVERSARIAL`** — the only class that closes anything |
| **Required first input** | **`release/orchestration/phase-2/REVIEW_8_CONTEXT_PACK.md`. Read it before anything else.** It exists by owner mandate (OD-P2-10 §1) so that independence means independent reasoning **plus complete relevant context**, not independent reasoning plus architectural ignorance. It states the trust model explicitly — which of protected machine state, owner-signed transitions, the T2 seal, git lineage, the floor document and environment variables carry authority — because previous reviewers had to infer it, and the orchestrator got it wrong twice by inferring. |
| Then | `GATES/OWNER-DIRECTION-P2-0009-*.md` (§5 decision rule, §6 the acceptance standard), `GATES/OWNER-DECISION-P2-0008-*.md`, `RESEARCH/P2-PROBE-OPTION-C.md`, `RESEARCH/P2-HISTORICAL-RULE-SOURCE.md`, `RESEARCH/P2-AR0096-POSITIVE-CONTROL-GAP.md` (a withdrawn orchestrator finding — reach your own conclusion, inherit neither position), `telemetry/checkpoints/P2-AR-0096.checkpoint.md` |

## 0. What is different about this review

**You are the convergence decision point** (OD-P2-09 §5). There is no automatic Review 9 on the same
mechanism-hardening loop. What happens next is determined by *what class* of thing you find:

| Your outcome | What follows |
|---|---|
| No HIGH blocker | freeze → mint `cap2-candidate-2` → fresh formal Phase-2 verification |
| HIGH in a **new optional/recovery mechanism** | that mechanism is **deleted or narrowed**, not wrapped in another guard |
| Material HIGH in an **old, untouched core subsystem** | **STOP** — returns to the owner as scope expansion |
| Only MEDIUM/LOW | Phase 2 does **not** stay open; classify, bound, disposition, proceed |

So **the class and severity of your findings matter as much as their existence.** Distinguish HIGH blocking defects
from bounded MEDIUM/LOW residuals from documentation/usability observations from deferred R2/R3 items. The owner has
stated the standard (OD-P2-09 §6): *"It is **not** 'no conceivable defect can ever be found in future.' Do not
transform a finite engineering acceptance criterion into an impossible claim of absolute security."*

**A competent reviewer finding a LOW or MEDIUM does not make this architecture unfit.** Equally, an unfounded green
ships a defect. Only the evidence is acceptable.

## 1. What this round did — deletion, for once

Read §9 of the context pack for the verified detail. In short: `gov floor-reanchor` is **deleted whole**, taking
AR94-C2, C3, C4, D1, D5 and the **confirmed** C5 concurrency race with it (C5 is *moot, not fixed*). The
`(device,inode)` marker binding and its GC are deleted, replaced by creator liveness. Relocation is now ordinary
governed re-onboarding that mints a **fresh** identity from unchanged code. Suite **368/368**.

Eight consecutive reviews have found something, and the standing pattern — recorded in the pack §6 — is that **each
repair's new mechanism became the next round's defect** (AR91→AR92, AR93→AR94). This round added almost nothing new,
which changes where you should look: **at what the deletions no longer protect**, and at the two genuinely new
things (`has_local_adoption_anchor` + the relaxed gate, and `union_last_known_rules_across_store`).

## 2. Priority targets — derived from what changed, not from a predecessor's framing

1. **The relaxed onboarding gate.** `if !already_installed || (already_installed && !has_local_adoption_anchor(root))`
   now permits a floor **rewrite** on an already-installed repository. That is a new path into an authoritative
   write. Can an ordinary project-scoped actor *cause* `has_local_adoption_anchor` to read false, and thereby induce
   a re-derivation from a shape they control? The gate sits behind `install_kernel` authority — test whether that
   holds on every route in. Verify AR88-C10B is not reopened (`mv src elsewhere && gov init --force` on an *unmoved*
   checkout must keep the anchor true and the gate false).
2. **The union spliced into `contract["paths"]`.** The builder measured that unioning into the floor alone produced a
   self-inflicted D027 finding, and fixed it by splicing the same restored rule objects into the **governed** paths
   array. Scrutinise that: can a restored pattern from *another project's* store entry reach a place where it grants
   rather than restricts? The union is claimed additive (`fresh` wins on conflict) — verify the claim rather than the
   comment, and probe what happens when two entries disagree about the same pattern.
3. **The creator-liveness residual**, builder-named and left open deliberately (pack §9a.1). Judge whether declining
   to add a process-state check was right. Note the argument *for* declining is the owner's own simplification
   principle; the argument against is that an attacker's own live process is a cheap precondition.
4. **`ar94_nc2`, rewritten by the builder** (pack §9a.3). A builder revising its own positive control is exactly what
   needs independent eyes. Does it still prove a genuine sandbox is honoured while its creator lives **and** that
   both a dead-creator and an unrecorded sandbox are refused? Build your own control if you doubt it.
5. **The two full-suite-only flakes** (pack §9a.4), both fixed test-only. Satisfy yourself neither masked a product
   defect — the builder's case is that the probe panicked before reaching `is_health_sandbox_root`/`creator_is_alive`
   at all.
6. **Scenario sandboxes have no floor** (pack §9a.2, orchestrator-found): inside `execute_check`'s `git: true`
   sandbox, lineage can never match, so the floor is *always* refused. Decide whether that is intended.

## 3. Verify the deletions did not remove protection

This is the inverse of every previous round's question, and it is the one this round most deserves. `floor-reanchor`
is gone and its tests with it. AR94-C5's race is moot. Confirm that:

* nothing that used to be refused is now permitted — in particular that a **planted floor document cannot gain
  authority** through the new re-onboarding path, which is where `floor-reanchor`'s worst finding lived;
* a second live checkout genuinely gets its own identity **without** disturbing the first (the claimed structural fix
  for AR92-C3 / AR94-C4);
* the AR92/AR94 reproductions that remain are genuinely closed, not merely orphaned by deletion.

## 4. Do not pass by gating everything

Independently re-run at minimum: `ar92_floor ar92_probe ar90_probe ar88_ ar94_floor ar90_floor
ar83_governed_widening multi_machine::clone_rebuilds_identical_derived_state
brownfield::brownfield_adoption_end_to_end p2ho56_floor p2ho56_closure p2_ar0096_reonboarding`.

All five OC-P2-04 cases must stay reachable and reportable; `floor_requires_product=false` must stay false; a
conforming pinned ELF must stay ungated **and running**; a genuine foreign clone must still bootstrap healthy.
**Property A is settled** (three consecutive reviews; `exec_resolve.rs` untouched here) — confirm preservation, do
not redesign.

**A guard that refuses everything passes every negative test. Build positive controls.**

The builder reports **368/368** in 3,631 s. Verify the figure against the tree; re-run the full suite only if you
change a product line or have reason to doubt it.

## 5. Discipline

Never `--test-threads=1`. Never pipe without `set -o pipefail`. Never bare `cargo fmt`. `. "$HOME/.cargo/env"` is
refused by the worktree guard — use `"$HOME/.cargo/bin/cargo"` directly. Never wait on the coordinator: bounded
iteration count and deterministic timeout action on every wait; prefer waiting on file content; if you match
processes, prove the waiter cannot match itself.

## 6. Return

A verdict — `SURFACE_SOUND` or `RESIDUAL_DEFECTS` — then: each finding with **severity and class** (per §0's table,
since the class determines what happens next), the reproduction you built, and whether it is new or a re-opening;
**each of the seven OD-P2-08 §8 stop conditions answered explicitly YES/NO with reasoning**; separate verdicts on
Property A and Property C; your ruling on §2.4 and §9a.2; what you could not probe; your commit SHA.

**If this surface is now sound, saying so is the most valuable thing you can do.** Three consecutive reviews found
Property A sound and said so plainly, and that is exactly how it should have gone.
