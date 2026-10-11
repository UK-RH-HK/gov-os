---
type: probe
task: DAEO-2lwj
reviewer_session: 826ab149-024c-441e-9e65-384f2dd6b396
implementer_session: 103940e7-a1af-472d-afbd-bbf8936f92b2
reviewer_wrote_nothing: true
commissioned_by: orchestrator
judged_by: orchestrator
judgement: pass
probed_commit: 249d67e378fc20ddf0cf7d3140f520e46d01e33f
---

# Probe record: W1-30 round on P-42 and P-43 (DEC-627, DEC-628, DEC-633, DEC-634, DEC-643)

- **What was probed.** The round's code at `249d67e3` on `w1/W1-30` (one session of a lead since
  `ef13a119`): `core-authority` declaring the policy key `human_gate` beside `authority`; the
  context-reproducibility check measuring the store's records of the ticket folder and no other record;
  this repository's hooks source generating the five registered hook entries. The branch was merged
  directly at the probed head.
- **Who.** A fresh reviewer session started by the orchestrator through `gov launch independent-auditor`,
  read-only, other than the implementer. It wrote nothing to the repository; the worktree was at
  `249d67e3` and clean of tracked changes when it left.
- **What held.**
  - Gate rule, 31 stand-in projects through `gov check`: every shape of a citation of a package that is
    not accepted is red, an accepted one green; an open ticket under a dead package is red; with the
    check's command missing or failing the check itself is red; no other policy finding disappears.
  - Context check, 22 stand-in projects: a ticket file the store does not hold, a broken one, one in a
    subfolder, one added after the load are red and named; nothing measured is not green; the kernel's
    template ticket leaves the measurement in both layouts and nothing leaves with it.
  - Hooks source: five events with the matchers, commands and time limits of the guard's listing; no
    Stop, no SubagentStop; rulesync drops nothing of the source.
- **Findings and their judgement (DEC-643).** All lesser, named residuals in
  `governance/project/bootstrap.md`: the authority check reading "the decision checker could not run" as
  green (older code); the gate rule reading the last commit; a copied ticket that kept another id; ticket
  files not ending in `.md`; non-record Markdown files of the ticket folder keeping the check red.
- **Judgement.** Pass: no fail-open hole that ordinary work produces, nothing that breaks a Wave 1 exit
  criterion (DEC-584).
