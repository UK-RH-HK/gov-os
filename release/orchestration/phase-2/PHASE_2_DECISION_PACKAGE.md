# Phase 2 decision package — `cap2-candidate-1` rejected, owner review required

| Field | Value |
|---|---|
| Date | 2026-09-21 |
| For | the product owner |
| From | the Phase-2 outer orchestrator (routing and recording only; it issues no verdict) |
| Candidate | **`cap2-candidate-1`**, commit `0bad524`, `product_code_digest` `e6332fc7…2220`, `governed_state_digest` `3d2aeba2…20c0` |
| Verdict | **`GOVERNANCE_CAPABILITY_BASELINE_REJECTED`**, issued by P2-AR-0052, a fresh independent synthesis verifier (the sole issuer) |
| Evidence | `release/capability-baseline/verify-1/` (nine runs); verdict and matrices in `verify-1/synthesis/` |
| Status | Phase 2 **stopped** under your instruction of 2026-09-20. No repair iteration 2 started, no further agents spawned. |

## 1. What was decided, and how far it got

Thirteen of the sixteen acceptance criteria hold. Three do not: **AC-3, AC-4, AC-5**.

| Holds | Detail |
|---|---|
| AC-1, AC-2 | All 101 capabilities have a status: 73 fully present, 28 partial, **none absent or unclear** |
| AC-6 | Qualification-oracle format accepted by a fresh reviewer |
| AC-7 | An executable, evidenced path to a provisional retrieval profile exists (no profile selected — that is Phase 3) |
| AC-8 | Artifact-flow coverage matrix rebuilt and all three failure conditions disproved |
| AC-9, AC-12, AC-13 | Candidate frozen; evidence fresh and independent; contract-binding chain faithful (1026/1026 lines carried verbatim) |
| AC-10 | Every capability names evidence that actually runs: 798 owners, none unresolved |
| AC-11 | Every capability carries its qualification challenges |
| AC-14 | Phase-1 root-of-trust acceptance still valid for this candidate |
| AC-15 | Regression green: unit 276/0, certification 207/0 (reproduced by me and by the synthesis verifier) |
| AC-16 | Every stated cross-capability interaction exercised end to end |

| Fails | Why |
|---|---|
| **AC-3** | Eight capabilities are partial in a way that could undermine advanced qualification: A1, S4, S5, C8, F3, F4, O5, U |
| **AC-4** | The plugin trust boundary is sound, but the tool-installation half of the same capability is not |
| **AC-5** | The health scheduler meets ten of twelve required behaviours; result provenance and the full-suite tier duty are not met |

## 2. The seven blocking defects

| # | What is wrong | Consequence | Class |
|---|---|---|---|
| 1 | The tool-install check reads each command argument separately, so wrapping effects in one string (`sh -c "sudo …"`) hides them | An install-authority role can put an arbitrary command on the trusted surface **without your gate**; proven by execution | **BC-P2-53 (new)** |
| 2 | The security review is bound to a tool's name and version, not to the installation it authorises | One review covered six descriptors; the one whose command was swapped after review installed ungated and ran | BC-P2-41 |
| 3 | Three project overlay files — permissions, path map, sensitivity — are read directly, bypassing policy precedence | A hand edit, with no command, transaction or gate, flips an authority decision; the audit says nothing | BC-P2-45 |
| 4 | Adoption stalls on exactly the kind of repository it targets: the OS classifies files as secret, never records that, then hard-blocks its own migration | Stages A6–A11 unreachable without hand-editing a file | BC-P2-33 |
| 5 | `gov update` answers "already up to date" from the candidate's **unauthenticated** version string before verification | A tampered, foreign-signed or below-floor release is answered "ok" — a false all-clear, not an installation | BC-P2-37 |
| 6 | Failure memory declares four record kinds (bugs, failed approaches, wrong assumptions, migration failures) that nothing can write | Work generation is built on records that cannot exist | BC-P2-32 |
| 7 | A tier run evaluates 39 of 74 declared checks and reports itself complete | Health can read GREEN while the same output reports the repository degraded | BC-P2-07 |

Defects 1–3 are one surface and compound: they are the trust boundary around installing executable tools.

## 3. Convergence — where the loop actually stands

- **Iteration-0 inventory (52 classes): 37 closed, 14 partially closed, 1 untouched.** Of 193 original findings, 142 are closed.
- **Six classes still leave a criterion unmet:** BC-P2-07, -32, -33, -37, -41, -45.
- **One genuinely new class: BC-P2-53**, so `introduces_materially_new_blocker_classes: true`.
- **Convergence counter: 1 of 3.** Escalation is mandatory only if three consecutive iterations each introduce new classes.

The verifier checked both consequential labels in the direction that would have *reduced* the count and refused to shade either: BC-P2-53's mechanism did not exist in the previous candidate, and the overlay-precedence defect is the previous class incompletely fixed, not a new one.

## 4. My assessment of the failure's nature

Asked to classify: **primarily implementation, with one architectural question and one orchestration lesson.**

- **Implementation (five of seven):** BC-P2-32, BC-P2-33, BC-P2-37, BC-P2-41 and BC-P2-07 are each a requirement the sources already state, implemented incompletely. Nothing about them needs a new decision from you.
- **Architecture (one):** BC-P2-45, and through it BC-P2-53. The tool-install envelope compares what a tool would do against what the project already authorises — but the authorising documents live in the project and are editable without governance. The repair claimed this surface and covered two of five documents. Whether those documents should be OS-protected state, or whether the envelope should be derived from something else entirely, is a boundary question worth your view even though the verifier ruled it an ordinary repair requirement.
- **Orchestration (a lesson, not a defect):** the new class sits in code written in the last round, to implement your OD-P2-03 rule, and merged on builder claims with only my regression reproduction before the candidate was minted. The earlier rounds, which had more adversarial passes over them, produced no new class. If you authorise another round, the tool-install surface deserves an adversarial review **before** the candidate is minted, not only after.
- **Not evidence-related:** AC-10, AC-12 and AC-13 all hold. The evidence map now names 798 owners that genuinely run, and the verifiers re-ran each other's work and reproduced every figure exactly. The loop's evidence discipline is working; what it is measuring is not yet sound.

## 5. Your options

- **A — Authorise repair iteration 2.** Six workstreams over the repair delta, mostly non-overlapping: tool-install trust surface (1 + 2), overlay precedence (3), adoption (4), update ingress (5), failure memory (6), health tiers (7). Overlay precedence must land before or with the tool-install work, because the latter's "trusted state" depends on it. Then a new candidate and a fresh verification. This is the default continuation and needs no change to any accepted source.
- **B — Amend the gate contract or a class's lifecycle placement.** Yours alone to do. For instance, deciding that the update-ingress report or failure-memory gap belongs to R2 certification rather than the Phase-2 baseline would change what must hold now. I would record the amendment, re-hash the frozen contract, and a **fresh** verifier would re-adjudicate the affected criteria on the same candidate — I would not re-grade it myself.
- **C — Meta-review the loop.** A fresh reviewer over the handoffs, round structure, evidence standard and my routing, as Phase 1's root-of-trust escalation did. Worth considering if you think four repair rounds should have produced a sounder result than this.
- **D — Stop Phase 2 here.** The release stays uncertified; Phase 3 is not started.

I recommend **A, with two conditions**: sequence overlay precedence first, and give the tool-install surface an independent adversarial pass before the next candidate is minted. If you also want the architectural question in section 4 settled, answer it as part of A rather than separately — it shapes what WS-A can rely on.

## 6. What is preserved

Everything is committed on `release/4.1.6-rc1`: the candidate tag, all nine verification runs with their held-out suites, the matrices, the repair delta, checkpoint `P2-CP-0011` and continuity handoff `P2-HO-ORCH-0003`. State verifies consistent. Nothing will move until you say so.
