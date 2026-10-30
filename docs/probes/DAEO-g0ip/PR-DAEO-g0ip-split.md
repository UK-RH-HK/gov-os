---
type: probe
task: DAEO-g0ip
reviewer_session: f109df90-b93e-46ba-a678-b2557c977a93
implementer_session: 841dfb85-9565-40ba-b1d4-22aa2e876b42
reviewer_wrote_nothing: true
commissioned_by: orchestrator
judged_by: orchestrator
judgement: pass
probed_commit: a2bc5e35d22f15a125c86728e1015ac485fdd91b
---

# Probe record: W2-01, the split (DEC-754), a judgement-only re-probe

DEC-754 (the orchestrator, applying the owner's DEC-750 item 2, 2026-10-17) splits W2-01. It narrows failure line 3 of the card to the cases its acceptance suite holds, and moves round 4's findings 1, 2 and 3 and package P-5 to W2-53 (DAEO-7rr2). W2-53 measures a later merge against git's own merge of its parents. This record judges the head against the narrowed card. It is not a fix round: no code or test changed after `09a01912`.

- **What was probed.** A judgement-only re-probe of DAEO-g0ip at `a2bc5e35`, against the ticket card as DEC-754 narrowed it. Since the round-4 head `09a01912` only `docs/` has changed. The W2-01 acceptance suite (88 passed) and `tests/unit/close/` (380 passed) were run to their end on this worktree's `src/`. Nineteen temporary repositories were built from scratch with the suite's support module, and `gov close` was run in each. They cover each case of narrowed failure line 3:
  - hand-resolved inward merges under the ticket's task, another task or none;
  - merge-backs that change, drop or replace probed code, acceptance tests or the ticket file, including an octopus and a merge-back made from a branch started before the earlier merge-back;
  - later merges holding the probed commit that rewrite, remove, rename or change the mode of probed code present in all parents.

  Two controls were also run: a round-4-style later merge, and an unchanged-code merge in and back.
- **What it found.** Every case of narrowed failure line 3 refused the close, with the probe gate naming the merge at fault. One case had several such commits; there the gate reported the newest first, and the close still refused. The unchanged-code control closed. The round-4-style control also closed: a later merge naming another ticket took that branch's side, made before the merge-back, and dropped a probed file. That is the kind of case DEC-754 gives to W2-53 (DAEO-7rr2), not one the narrowed card holds. Round-4 findings 1, 2 and 3 and package P-5 moved to W2-53 under DEC-754 item 2 and were not judged here. No other case was found that loses work, lets an implementer change acceptance tests, or makes the gate or `gov close` fail open.
- **Judgement.** pass. The code at `a2bc5e35` meets every KPI line of the card as DEC-754 narrowed it. Each case narrowed failure line 3 names refuses. What still fails open (a later merge measured against git's own merge of its parents) is W2-53's under DEC-754.
