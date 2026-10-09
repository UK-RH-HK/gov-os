---
type: probe
task: DAEO-cdoi
reviewer_session: 2020c8c7-b490-4464-8b39-64fc3030412a
implementer_session: bee7ea18-6d7b-4a25-883b-49f2374ff011
reviewer_wrote_nothing: true
commissioned_by: orchestrator
judged_by: orchestrator
judgement: pass
probed_commit: 920229dc8b0eec1ddeb888a4e4237bb119db2330
---

# Probe record: W1-41 (`gov adopt --lite`, the legacy importer, external references in the context)

- **What was probed.** The ticket's code at `920229dc` on `w1/W1-41` (the lead's third run, session
  `bee7ea18-6d7b-4a25-883b-49f2374ff011`). A fresh read-only reviewer (role `independent-auditor`, session
  `2020c8c7-b490-4464-8b39-64fc3030412a`, 2026-10-09), commissioned and judged by the orchestrator (DEC-137),
  built throwaway projects in its session's temporary folder, ran the stages against them and wrote nothing
  in the repository; `git status --short` of the worktree was the same before and after. Move stages were
  run with the importer lookup replaced in memory, because the sandbox cannot run the code-graph tool:
  importer behaviour was not observed.
- **What it found.** Ten findings, each reproduced. The ticket's four failure lines hold as observed (no
  content change in a batch, no move without the A5 verdict, no legacy rule file left loaded, no unknown
  artefact moved or deleted). One fail-open in a shape ordinary work produces: a legacy memory store was
  retired while a kept rule file still cited it behind a path prefix.
- **Judgement (DEC-552, under DEC-498): pass, with one fix round and recorded residuals.** Three behaviours
  were fixed after the review (commits `ba541f4e`, `a9e8f0f0`; head `868d72b9`; DEC-568): a citation behind
  `./`, `/`, `../` or a folder holds the store back; every record that still stands holds it back; a ticket
  whose sources are all external is refused whatever its dependencies name. There was no second probe: the
  fix is 17 lines added and 8 removed, each refusing more, read by the lead and the orchestrator. The other
  findings are residuals in `governance/project/bootstrap.md` ("W1-41").
