---
type: probe
task: DAEO-3ef2
reviewer_session: 2f6dc4ca-08b6-4809-b699-7df67b8cbf01
implementer_session: 510489f0-473e-4313-991d-f1caa175fe3b
reviewer_wrote_nothing: true
commissioned_by: orchestrator
judged_by: orchestrator
judgement: pass
probed_commit: 8ad901d579ce858ad38020e5a4dcf0a54628de76
---

# Probe record: W1-38 round, the held-out step in the adapter check (DEC-635, DEC-641, DEC-644)

- **What was probed.** The round's code at `8ad901d5` on `w1/W1-38` (one session of a lead since
  `09207f4d`): the adapter-portability check applying the existing generator's held-out step to the
  settings it generated in its temporary folder, before it compares. The branch was merged directly at
  the probed head.
- **Who.** A fresh reviewer session started by the orchestrator through `gov launch independent-auditor`,
  read-only, other than the implementer. It wrote nothing to the repository; the worktree was at
  `8ad901d5` and clean when it left.
- **What held.** On stand-in projects built from scratch, with invented held-out paths:
  - with a held-out file, "generated, then the step" is green; the step never run, a rule lost, a rule
    the file does not give, the rule under another list or tool, another pattern form, a duplicate,
    another order and another byte form are each red on the settings;
  - without a held-out file the check's exit code and output are byte for byte those of the code before
    the round, on ten states;
  - every broken state of the held-out file is red and none falls back to a comparison without the step;
  - nothing printed, by the check or by `gov check --json`, holds a stand-in path; no traceback;
  - the step writes only in the temporary folder.
- **Findings and their judgement (DEC-644).** None for the merge. Lesser, named residuals in
  `governance/project/bootstrap.md`: a held-out file without a settings source can never be green; the
  finding on the settings does not mention the step; one code for two causes; the check and the
  generator run by hand may take different project roots.
- **Not probed, by the brief.** This repository's own settings: measured by the orchestrator's
  counts-only comparison and the owner's apply step (DEC-640, DEC-645).
- **Judgement.** Pass: no fail-open hole that ordinary work produces, nothing that breaks a Wave 1 exit
  criterion (DEC-584).
