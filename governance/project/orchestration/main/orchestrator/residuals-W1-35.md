
## W1-35 residuals (the four method skills: discovery, planning, test design, change, 2026-10-07)

- **Built:** four skill files under `template/governance/kernel/skills/` (discovery, planning, test-design,
  change), each with a versioned frontmatter, within the size limits, citing the decision or capability it
  follows and granting nothing; and the check declaration `skill-regression-a`, which runs W1-26's generic
  skill validator over the four folders.
- **The suite tests the text of the skills, not sessions that follow them.** These KPI clauses are measured
  only by a live session and go to the Wave 1 exit run (W1-42): "0 of the decision packages discovery asks
  are answerable from files its retrieval bundle cites" on the MR-A-02 and MR-B-02 dev scenarios; "its
  transcript reads no file outside them" for test design; "planning emits schema-valid tickets and one linked
  gap ticket per required open readiness row"; the change skill's refusal to archive a kernel change that
  lacks a record; the impact assessment run from a plain-language question. Until then they are unmeasured,
  not met.
- **The declaration's command names paths under `template/…`,** which an installed project does not have (its
  skills are under `governance/kernel/…`). True of every declared check today: for the adoption tickets
  (W1-39, W1-41).
- **The first return declared the check with the command `true`,** because the validator did not exist yet
  (DEC-439 reopened W1-26 for it). The second return runs the real validator.
- **W1-26's fixture was revised for this ticket:** a project built by W1-26's suite now holds the kernel's
  skill folders, copied generically, since a check that finds no skill is unmeasured and red (DEC-425). No
  assertion was changed.
- **Records:** the merge-back `84bf8d12` was made with git's `ours` preference after the plain merge
  conflicted on W1-26's README (the branch's file had been aligned to the integration branch's version plus
  its own lines); the containment check flagged that merge for its own change to that README, and an earlier
  merge `91568f75` for the shared W1-07 support file. Both are byte-level outcomes of aligned files.
- **Learning metrics:** two lead starts, plus two short test-designer turns started by the orchestrator (the
  fixture, the alignment); 112 cases; no reviewer round (STANDARD, self-review); about 200 lines of skill text
  and a 5-line declaration.
- **Regression at `ab1fa23c`:** REGLINE
