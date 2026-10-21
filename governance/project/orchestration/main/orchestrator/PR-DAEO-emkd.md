---
type: probe
task: DAEO-emkd
reviewer_session: cc784d3e-ecb5-4176-8726-847f86f79cf6
implementer_session: 3c1e5fff-9b45-4e0e-982e-bd2e8f02cf46
reviewer_wrote_nothing: true
commissioned_by: orchestrator
judged_by: orchestrator
judgement: pass
probed_commit: e9e6ee255a095c67a0e90c7471b6f2dd548ddfbe
---

# Probe record: W1-02 follow-up (the guard refuses reads of the two protected files)

- **What was probed.** The follow-up's code at `e9e6ee25` on `w1/W1-02` (the lead's third run, session
  `3c1e5fff-9b45-4e0e-982e-bd2e8f02cf46`): the read rule, its copies and second names, and the hook-listing
  helper. A fresh read-only reviewer (role `independent-auditor`, session
  `cc784d3e-ecb5-4176-8726-847f86f79cf6`, 2026-10-09), commissioned and judged by the orchestrator (DEC-137),
  worked on a stand-in world in its session's temporary folder, in-process and through the hook program, and
  wrote nothing in the repository; `git status --short` of the worktree was the same before and after.
- **What it found.** Eleven findings. One read gets through in a shape ordinary work produces: a shell search
  from the root with a name filter that names or matches a protected file. Five more reads get through in
  deliberate or unusual shapes; some patterns get no answer in time; the helper prints a deny path for rule
  shapes the project's writer does not produce. No ordinary work is newly stopped (about 170 daily calls
  tried). A shell command with a tilde and a NUL byte is refused (exit code 2).
- **Judgement (DEC-562, under DEC-498 and DEC-557): pass; merged as probed.** The integration branch held no
  read rule before, so the merge refuses more in every case. The ordinary-shape finding, the bounded answer
  time and the NUL byte are built in the round the owner ordered directly after this merge (DEC-557), test
  designer first, with that round's own probe. The others are residuals in `governance/project/bootstrap.md`
  ("W1-02 follow-up").
