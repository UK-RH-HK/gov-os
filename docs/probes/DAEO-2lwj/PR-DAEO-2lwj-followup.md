---
type: probe
task: DAEO-2lwj
reviewer_session: 2e97ad0c-eee6-4500-baae-303e79f117f7
implementer_session: 9e9a7dc8-1be2-4138-87a8-c80fe86a1f53
reviewer_wrote_nothing: true
commissioned_by: orchestrator
judged_by: orchestrator
judgement: pass
probed_commit: c52de7c2213786a303a19d5d7930515760759ad4
---

# Probe record: W1-30 follow-up (the parallel test runs of `gov close`)

- **What was probed.** The follow-up's code at `c52de7c2` on `w1/W1-30` (the lead's second run, session
  `9e9a7dc8-1be2-4138-87a8-c80fe86a1f53`): the parallel runs, the serial-only list and its plugin, the two
  settings in the path map, `gov rebuild --no-embeddings`. A fresh read-only reviewer (role
  `independent-auditor`, session `2e97ad0c-eee6-4500-baae-303e79f117f7`, 2026-10-09), commissioned and judged
  by the orchestrator (DEC-137), built its own projects in its session's temporary folder and wrote nothing
  in the repository; `git status --short` of the worktree was the same before and after.
- **What it found.** Nine findings, each reproduced or read. "No case is lost in any shape ordinary work
  produces." Two shapes close a ticket on a failing acceptance case and need a deliberate or unusual input:
  a serial run of declared cases that ends with exit code 0 and no result, and a project file named like the
  close's own plugin. The rest are lesser (workers that outlive a time limit, counts, records, tracebacks).
- **Judgement (DEC-555, under DEC-498): pass, without a fix round.** No fail-open hole and no silent close
  in a shape ordinary work produces. Five findings are built in the follow-up after W1-41, test designer
  first; the others are residuals in `governance/project/bootstrap.md` ("W1-30 follow-up: the parallel test
  runs"). Until that follow-up merges, the orchestrator reads the `test_runs` of every close.
