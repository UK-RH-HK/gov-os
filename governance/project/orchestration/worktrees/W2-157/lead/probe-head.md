---
type: probe
task: DAEO-ozyt
reviewer_session: 7087bb80-3399-4558-b2b8-329f6b0dd9d8
implementer_session: "eng-1-2 bada15f5-de56-4438-958f-cc3416e0acb3 (8939fcff5515, c5b0ee91dd12); eng-2 09b6ec9c-efe6-40f8-8c65-a2804b1bfb3e (1c2ad5b9c6ef); eng-3 71777e66-34d9-4fc1-9259-75f870e88b36 (365a4acda69b)"
reviewer_wrote_nothing: true
commissioned_by: orchestrator
judged_by: orchestrator
judgement: pass
probed_commit: 365a4acda69b7bf1ce98009b3003719f16b0ecaa
---

# Probe record: W2-157 (DAEO-ozyt) the GPU backstop in the product, STANDARD review, rounds 1 and 2 of 2 (DEC-1010)

- **Round 1** (reviewer session 4ad4ff19-4cc0-4b86-b9d9-eec361b11b9d, independent-auditor, Opus high, read-only) probed
  head `1c2ad5b9c6ef`: **fail** (`verdict.ready`: S1 marked fail and FR-1 blocks, in scope, ordinary work, fails open;
  S4 marked fail). FR-1/FR-2: a backstop running inside a group it names froze itself before it paused the groups named
  after that one, and before it wrote the TRIP line and the inbox item.
- **The repair:** the lead settled the wanted behaviour as L5b (the backstop's own group, when named, is paused last,
  after every other named group, the TRIP line and the inbox item; a `note:` line in the item; resuming the own group
  lets the command end). The independent test designer added 7 acceptance cases for it (`ca7f8e689f2d`,
  `c4107a6d6cee`, merged at `97e44155c5e1`, 6 red on the built code); a fresh engineer fixed `backstop.py` and added
  FR-5's sentence to the evidence's operator step (`365a4acda69b`). Round 1's FR-3, FR-4 and FR-6 to FR-10 were judged
  out of scope and stay as residual rows.
- **Round 2** (reviewer session 7087bb80-3399-4558-b2b8-329f6b0dd9d8, independent-auditor, Opus high, read-only, a fresh
  session) probed head `365a4acda69b`: **pass**, `verdict.ready` True: every KPI line S1-S5 and F1-F4 pass; FR-1 and FR-2
  fixed; three new findings, none blocking: FR-11 (medium; in scope, not ordinary work, fails open: with the own group
  named, an inbox item that cannot be written at the trip crashes the command before the own group is paused), FR-12
  (low; in scope, ordinary work, other: with the own group named the watch never ends on its own), FR-13 (low; in
  scope, ordinary work, other: the root is not checked to be a project at the start). No third round (DEC-1010).
- **The lead's checks of the probed head:** `gov accept W2-157` 116 passed, 0 failed (every KPI line); the scoped verify
  (`lead_verify.sh`) 4167 tests, 7 failed, every one outside this ticket: the six W2-96 signal reds (shared base reds,
  ruling P-W2-121-5; W2-177 fixes them) and W2-02's `green_here` core-schema case on `.tickets/DAEO-1k7y.md` (W2-177's
  ticket file in the base; this branch changes no ticket file).
- **Residual rows the lead names:** FR-11 (a `try`/`finally` so the own group's SIGSTOP happens whatever the item write
  does), FR-12, FR-13; round 1's FR-3 (a GPU that cannot be read leaves the watch blind with no inbox item: an owner
  question), FR-4, FR-6 to FR-10.

The two reviewers' returns follow verbatim, round 1 first; the last verdict block (round 2's) decides.

## Round 1: the reviewer's return (head 1c2ad5b9c6ef)

