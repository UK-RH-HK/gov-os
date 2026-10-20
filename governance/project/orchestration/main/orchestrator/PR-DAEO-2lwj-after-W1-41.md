---
type: probe
task: DAEO-2lwj
reviewer_session: 671388f7-f3a9-426f-9c6c-dee47dd1ffc8
implementer_session: bed09442-6576-472a-96c0-eef2049e7072
reviewer_wrote_nothing: true
commissioned_by: orchestrator
judged_by: orchestrator
judgement: pass
probed_commit: 83d11b2d0c678404d42109f46f860aade837b5b6
---

# Probe record: W1-30 follow-up after W1-41 (DEC-569, DEC-572, DEC-579 to DEC-581, DEC-586)

- **What was probed.** The follow-up's code at `83d11b2d` on `w1/W1-30`, three runs of a lead since
  `e12df900` (the last run's session is `bed09442-6576-472a-96c0-eef2049e7072`): the cost counter in the
  close, the probe gate (DEC-581), the READY rule (DEC-544), the records query, the refusal of a named
  register absent from the commit, the checks of an installed kernel, containment's reading of a merge
  commit's ticket file (DEC-572), and the time limit in the kernel template's settings (DEC-580). A fresh
  read-only reviewer (role `independent-auditor`, session `671388f7-f3a9-426f-9c6c-dee47dd1ffc8`,
  2026-10-09), commissioned and judged by the orchestrator (DEC-137), read the diff, called the gates on
  stand-in projects in its session's temporary folder, and wrote nothing in the repository. It did not run
  a whole `gov close` end to end and did not read the READMEs of W1-26 and W1-50.
- **What it found.** No fail-open hole that ordinary work produces. Ordinary work stopped, failing closed:
  the probe gate refuses a merge of the integration branch into the ticket branch after the probe, merged
  back; `gov check` in a project with the installed layout only is red until its checks can be measured,
  where it ran nothing before. Fails open by a slip or a malformed file only: a `Task:` trailer with unusual
  spacing escapes the gate; a merge of the probed commit that drops probed code by a hand-resolved conflict
  passes; `allowed_paths` written twice. Containment held in every case tried; the store load and the READY
  rule held for the main shapes; the template's three hook entries carry the limit and nothing else changed.
- **Judgement (DEC-592, under DEC-498 and DEC-584): pass, no fix round.** This was the last run of the
  follow-up; each finding is a named residual in `governance/project/bootstrap.md` ("W1-30 follow-up after
  W1-41"). The orchestrator probes a branch's final head and merges it directly until the gate's reading of
  a merge back is widened.
