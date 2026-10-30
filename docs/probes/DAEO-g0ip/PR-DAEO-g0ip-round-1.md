---
type: probe
task: DAEO-g0ip
reviewer_session: 37361002-ac68-4a93-904b-381c99872377
implementer_session: e37439d8-c23a-4ece-8a2c-5b51b291c020
reviewer_wrote_nothing: true
commissioned_by: orchestrator
judged_by: orchestrator
judgement: fail
probed_commit: 8b479c1b249f87bb6946a4b142101cd28b090d5c
---

# Probe record: W2-01, round 1 (`gov close` and traceability: trailers base, merge form, owner-accepted history, the probe gate after a merge-back)

- **What was probed.** Head `8b479c1b249f87bb6946a4b142101cd28b090d5c` of `w2/W2-01` (DAEO-g0ip), running this
  worktree's `src/` (engineer session `e37439d8-c23a-4ece-8a2c-5b51b291c020`, commit `7ebe5489`). A fresh
  read-only reviewer (role `independent-auditor`, session `37361002-ac68-4a93-904b-381c99872377`, 2026-10-16),
  commissioned and judged by the orchestrator (DEC-137), wrote nothing in the repository (`git status --short`
  empty before and after). The W2-01 acceptance tests passed (46), and with the close unit tests 411 passed.
  Then 35 history-module cases in throwaway repositories, and 16 `gov close` and trailers-check runs in temporary
  projects built with the suite's own support module, covering: how accepted-history entries are resolved
  (status and owner wording, which commit is named, abbreviated or ambiguous ids, register forms); where the
  trailers base can point, and the base-move report; the merge form (deletions, one-side resolutions, clean
  shared-file merges, octopus merges, unrelated histories); the probe gate after merge-in and merge-back,
  including drops, "ours" merges and integration-side resolutions; probe rounds.
- **What it found.**
  - A merge-back that drops or replaces probed code passes the probe gate (a probed file resolved to the
    integration side, a probed file removed, an "ours" merge). In KPI 4's own merge-in-then-back layout, the
    close passes with a probed file deleted; the earlier rule refused that case.
  - A merge-form merge that deletes the ticket's work passes the trailer gate.
  - A clean merge of a file both sides changed is wrongly refused as having its own change.
  - Owner recognition accepts "owner-delegated" wordings, a superseded or revoked owner status, and an owner
    status quoted in another entry's body; "names the commit" is an eight-character substring match.
  - Lesser issues in the base-move report and in close-versus-check differences; a commit of another ticket
    after the merge-back may change probed code (DEC-490, unchanged by this ticket).
  - Base, register, ambiguous-id and probe-round handling fail closed as required.
- **Judgement.** fail. In ordinary merge-back work, the probe gate passes on changed or deleted probed code, and
  the trailer gate passes a merge that carries its own change (the ticket's work removed). Both fail open and
  can lose work at close. The orchestrator ordered a fix round (test design, engineer) and a second, last review
  (DEC-413).
