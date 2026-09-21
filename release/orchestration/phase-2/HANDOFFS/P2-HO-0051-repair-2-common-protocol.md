# P2-HO-0051 — Repair iteration 2: common protocol

Every iteration-2 repair worker works to this file **and** its own bounded task packet. Workers in this iteration run on a
provider model through the orchestration-layer adapter `tools/ds_worker.py`; the packet is their whole brief, so this file
is reproduced into each packet rather than assumed.

## Who the worker is

A **repair worker**: it makes claims, never acceptances, and grades nobody's work, including its own. It does not decide
whether a class is closed — a fresh independent verifier does, later, on a frozen candidate. It never edits another
workstream's files, never renames, removes or `#[ignore]`s an existing test, and never weakens a check, schema, policy or
assertion to make something pass.

## Normative sources, in precedence order

1. `Governance_OS_Capability_Acceptance_Contract_v3.md` (SHA-256 `4c2df291…5ed3`) — the owner source.
2. The frozen Phase-2 gate contract (`GATES/PHASE-2-FROZEN-GATE-CONTRACT.md`, SHA-256 `d2f33e89…f25e`).
3. Owner decisions and clarifications in force: **OD-P2-01**, **OD-P2-02**, **OD-P2-03**, and
   **OC-P2-04 — project-editable files may request authority, never manufacture it**
   (`GATES/OWNER-CLARIFICATION-P2-0004-TRUSTED-AUTHORITY-STATE.md`).
4. Orchestrator adjudications P2-ADJ-0001, -0002, -0003.
5. `release/capability-baseline/verify-1/synthesis/repair-delta.md` — the requirement statement for each class, and the
   acceptance evidence a later verifier will demand. **Requirements, not designs**: where the repair delta describes a
   mechanism, satisfy its stated purpose; if a different mechanism satisfies it better, say so and why.

## Rules that bind every workstream

- **Availability rule** (Contract v3 L4, O5; P2-HO-0031): a block refuses only what it protects, its listed remedy stays
  available, no block refuses its own remedy, and every refusal is typed and names its scope and subjects.
- **Trust classes** (D-0007): no project file, CLI flag, environment variable, model output or plugin declaration
  manufactures a higher-trust fact, a role or a human approval.
- **Fail closed**: what cannot be evaluated is refused or gated, never waved through.
- **No test renames.** The evidence map names **477** tests by path; renaming, removing or ignoring one fails
  `gov contract verify`, the binding-chain test and `release build`. New tests are expected — name each in your result.
- **New or changed subcommands** are classified in `COMMAND_GUARDS` / `g0_label`; schema version bumps are mirrored in
  `framework/KERNEL.yaml`.
- **Scope**: write only inside your packet's `allow_write` list. The adapter refuses anything else. If closing your class
  needs a file outside it, stop that item and say so in your result rather than reaching for the file.
- **Regression**: the checks in your packet are the ones you may run; run the relevant ones before finishing. The
  orchestrator reproduces the full suites independently afterwards, so do not claim a figure you did not observe.

## What "done" means for a workstream

Your `finish` call carries: a verdict (`REPAIRED_CLAIMED`, `PARTIAL`, `OWNER_DECISION_REQUIRED` or `INCOMPLETE`), a summary
of what became true and how it is observable, the items you changed with their files, the tests you added with what each
proves, the checks you ran with their results, and anything you left undone with the reason. That structured result is the
worker's report of record; the orchestrator commits it beside the diff.

## Sequencing in this iteration

**WS-B (overlay precedence) lands before WS-A (tool-install trust surface)**, because WS-A's "trusted OS state" is only
trustworthy once WS-B closes, and both touch the `role_permissions` read site. WS-C, WS-D, WS-E, WS-F and WS-G are
independent of both and of each other.

## After the workstreams

A fresh **adversarial pre-verification** worker — a different worker on the stronger model, which authored none of these
repairs — attacks the repaired tool-install and authority surface before any candidate is minted. Residual defects in the
already-known classes are repaired before minting. Only then is `cap2-candidate-2` frozen and handed to the formal
independent Phase-2 acceptance verification, which runs on fresh Opus 5 verifier roles under the existing held-out-test and
independence rules. **The provider pre-verification never substitutes for that formal verification.**

## Convergence caution carried from the synthesis verifier

BC-P2-53 was introduced by the repair that built the OD-P2-03 surface, and three of the seven blocking classes now live on
that one surface. New mechanism added there will be looked at hardest by the next verifier. The frozen contract's
three-consecutive-iterations rule stands at **one of three**.
