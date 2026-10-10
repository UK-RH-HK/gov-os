---
type: probe
task: DAEO-2lwj
reviewer_session: 28ebf8d8-a26b-4996-ab11-bd0856bb3a35
implementer_session: ffa15ad0-8fa4-406f-88a4-91699558c54d
reviewer_wrote_nothing: true
commissioned_by: orchestrator
judged_by: orchestrator
judgement: pass
probed_commit: 8e5c71a82588701f4d0b3c3d0570e58a35b79add
---

# Probe record: W1-30 fix round before adoption (DEC-612, DEC-613, DEC-616, DEC-620, DEC-621, DEC-622)

- **What was probed.** The round's code at `8e5c71a8` on `w1/W1-30` (two sessions of a lead since `f218b4e3`,
  `ebaeda6c-8c69-40ab-a26c-6527e848236c` and `ffa15ad0-8fa4-406f-88a4-91699558c54d`): the context check
  measuring records of type `task`; the runner giving no finding for the success form of a `gov` command;
  five record types in the schema check and the single finding for a missing shared field; the time limit
  of the retrieval-regression declaration; the `enforces` field and the policy rule that reads it alone;
  this repository's two rulesync sources; the ticket schema accepting either form of a dependency's id.
  The branch was merged directly at the probed head.
- **Who.** A fresh reviewer session started by the orchestrator through `gov launch independent-auditor`,
  read-only, other than the implementer. It wrote nothing to the repository; the worktree was at
  `8e5c71a8` and clean of tracked changes when it left.
- **What held.**
  - Runner: 28 output shapes run; nothing that was red or yellow is green except the success form at
    exit 0. Of the twenty declared checks only fresh-agent-reconstruction prints that form.
  - Schema check: the single-finding change drops no distinct finding.
  - Policy rule: every invalid or doubtful shape of the field fails closed; the old cover by a family's
    name is gone; `gov ci job` gives the same policy entries as `gov check`; `human_gate` stays red.
  - Context check: names what fails and stays not green, for both type names.
  - No reader of `depends_on` fails open on the record-id form.
  - The two rulesync sources are byte copies of the template's.
- **Findings and their judgement (DEC-622).** All lesser, named residuals in
  `governance/project/bootstrap.md`: a hard-block key covered by a declaration of any severity, tier or
  result; a record relabelled to one of the new types leaving the checks that select by type; the ticket
  schema's second form admitting any id of the ticket grammar; the success form with findings inside its
  result; fresh-agent-reconstruction green with no checkpoint found; the `change` check reading one
  commit only.
- **Judgement.** Pass: no fail-open hole that ordinary work produces, nothing that breaks a Wave 1 exit
  criterion.
