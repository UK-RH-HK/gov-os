---
type: probe
task: DAEO-emkd
reviewer_session: d527c0e4-c13b-4708-80ce-782dfa2b3348
implementer_session: 9079510e-fb0b-4e4a-929f-9c5102f1ee41
reviewer_wrote_nothing: true
commissioned_by: orchestrator
judged_by: orchestrator
judgement: pass
probed_commit: ae6d8a7446f4825e1e87ca7b260abb0264eb5eec
---

# Probe record: W1-02 follow-up, the held-out check's path limit and the guard's deadline (DEC-574, DEC-580)

- **What was probed.** The code of the lead's seventh and eighth runs at `ae6d8a74` on `w1/W1-02` (code head
  `60d1a4a8`; the eighth run's session is `9079510e-fb0b-4e4a-929f-9c5102f1ee41`): the held-out check that
  resolves no string longer than the system path limit (`b961686b`), and the PreToolUse hook program's own
  deadline of 20 seconds (`60d1a4a8`). A fresh read-only reviewer (role `independent-auditor`, session
  `d527c0e4-c13b-4708-80ce-782dfa2b3348`, 2026-10-09), commissioned and judged by the orchestrator (DEC-137),
  built stand-in projects in its session's temporary folder, ran the hook as a process, and wrote nothing in
  the repository; `git status --short` of the worktree was the same before and after.
- **What it found.** No fail-open that ordinary work can meet, in either change. Every forced failure of the
  deadline's mechanism ended closed (the decision's process killed, exiting with another code, stopped,
  flooding its output; `fork` or `pipe` failing; the hook's own streams closed); the deadline's value is a
  constant read from nothing; the refusal has the form of an ordinary refusal; nothing was left running
  after a deadline. An ordinary call costs 4 to 10 ms more and answers byte for byte as before; nothing
  ordinary came near 20 seconds (64 hooks at once, a loaded machine, a tree of 150,000 files). One read gets
  through by a deliberate shape only: a shell word longer than the path limit with a brace list of some 900
  alternatives, which the shell shortens itself. Lesser: the path limit has no lower bound of the guard's
  own; a hook started with the child signal ignored refuses every call; thin findings from the waiting
  process; a program that keeps the pipes open is left running.
- **Judgement (DEC-587, under DEC-498, DEC-577 and DEC-584): pass, no fix round.** This was the last run of
  the round; no finding is a fail-open hole that ordinary work produces, so each is a named residual in
  `governance/project/bootstrap.md` ("W1-02 follow-up, the held-out check and the guard's deadline"), the
  brace-list shape first among them, for the Wave 2 list.
