---
type: probe
task: DAEO-emkd
reviewer_session: ea1c1fed-b545-4461-b029-09dae6731851
implementer_session: abedf2a3-1c6c-41af-b729-aac4c6e73384
reviewer_wrote_nothing: true
commissioned_by: orchestrator
judged_by: orchestrator
judgement: pass
probed_commit: dc9fda1660008d96b54bb1e5b6ad25a74feeaccd
---

# Probe record: W1-02 follow-up, the root-search round (DEC-557, DEC-562)

- **What was probed.** The round's code at `dc9fda16` on `w1/W1-02` (code head `02d0b35b`; the lead's fourth
  run, session `abedf2a3-1c6c-41af-b729-aac4c6e73384`). A fresh read-only reviewer (role
  `independent-auditor`, session `ea1c1fed-b545-4461-b029-09dae6731851`, 2026-10-09), commissioned and judged
  by the orchestrator (DEC-137), built stand-in projects in its session's temporary folder, called the rule
  in process and through the hook program, and wrote nothing in the repository; `git status --short` of the
  worktree was the same before and after.
- **What it found.** A root search with a numbered redirect after it (`2>/dev/null`) was allowed and read
  both stand-in files, a shape ordinary work produces constantly. Smaller holes in ordinary shapes: a search
  after a shell keyword, a comment after the search, option groups with a digit, `egrep` and `fgrep`, a
  search behind `timeout` and its like. Thirteen deliberate inputs under the round's length bounds took 1 to
  190 seconds to decide, which fails open where the harness lets a timed-out hook through. Nothing got
  through by the fed search, a NUL byte or an exception.
- **Judgement (DEC-570, DEC-571, under DEC-498): pass, with one fix round and recorded residuals.** The
  holes above and the time bound were built after the review, test designer first (commits `ebf80764`,
  `10e6ef39`; head `02f0294d`). There was no second probe: the fix is 127 lines added and 22 removed in one
  file, each adding refusals or doing the same work with the same answer, read line by line by the lead and
  the orchestrator; over three seeds of 420,000 random calls no call that was refused is now allowed. The
  other findings are residuals in `governance/project/bootstrap.md` ("W1-02 follow-up, the root-search
  round").
