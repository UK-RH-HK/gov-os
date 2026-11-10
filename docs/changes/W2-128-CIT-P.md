---
id: W2-128-CIT-P
type: change-impact-proposal
status: ACCEPTED
state_class: EVIDENCE
date: 2026-11-09
branch: w2/W2-128
ticket: DAEO-t8mp (W2-128)
author: product-spec (W2-128, round 1)
review: one read-only independent reviewer, after the acceptance suite is green (CAP-33)
decisions_read: [DEC-1050, DEC-1052, DEC-1073, DEC-1083, DEC-1088, DEC-1092, DEC-1094, DEC-1109, DEC-957, DEC-959, DEC-963, DEC-1010, DEC-1014]
decisions_carried: [DEC-1050, DEC-1052, DEC-1073, DEC-1088, DEC-1092]
state: draft (round 1, the text half)
---

# W2-128: change-impact proposal (CIT-P) on the kernel templates, schemas and the engineer role line

This change gives the kernel one template per role, a ticket template and a brief envelope, filled from the ticket and
one project facts file (`governance/project/facts.yaml`). It touches kernel files (templates, schemas, a role line), so
it goes through CIT-P under CAP-33. The owner approved the scope when the ticket was filed (DEC-1081 (2), DEC-1050
TEMPLATES); the interface was stated before the pair started (DEC-1109 (2)). This record is round 1's draft: the text
half. Round 2 (the code half: `gov brief`, the ready check's refusals, the launcher flag) adds its own lines here.

## 1. What triggers the change (the evidence)

| # | Trigger | Source | Measured |
|---|---|---|---|
| T1 | Four layers of brief text disagree: the kernel `brief-*.md`, the CTO prompt's Appendix A, `LEAD-w2-common.md` ("they override the templates where they differ") and each lead's hand-written worker briefs | R3-1 (`governance/project/orchestration/packages/LIFT-1/R3-TEMPLATES.md`) | 82 gap lines on decision readings or contradictions |
| T2 | Leads write every worker brief by hand and copy the standing rules into it | R3-2 | 440 briefs, median 12,891 characters (p90 20,022); 324 carry a standing-rules section, a median 35 % of the brief |
| T3 | Role files never reach a launched session | R3-3 | 0 of 440 briefs pass `--agent` or `--append-system-prompt*` |
| T4 | Kernel texts state superseded rules (the engineer "until its acceptance tests pass", against DEC-957 and DEC-959; the test designer "does not read src/", against DEC-963) | R3-4 | the files named in §3 |
| T5 | The ticket format has no non-goals, no per-KPI check and no dependency fields | R3-5; DEC-1088 | 2 of 136 W2 tickets name non-goals; median ticket 3,824 characters |
| T6 | What briefs miss is facts (paths, commands), not rules; doing costs more than reading | R2 (`R2-BRIEFS.md`), R3 headline 3 and 4 | 511 brief-gap lines and 7,424 stated minutes in 83 returns; 24.5 % of tool calls are wait loops, 11.6 % ceremony; 343 hand-written verification wrappers; 218 harness denials; sessions with a guard refusal fell from 68 % to 17 % once briefs gave working command forms |
| T7 | Links are recorded nowhere by rule | LINK-INTEGRITY.md §5 (DEC-1073 (5)(c)) | D5-ROWS rows 10 to 17 |
| T8 | Lines that work showed missing | D5-ROWS rows 1 to 9 (DEC-1109 (2)) | each row's evidence in `D5-ROWS.md` |

**Corroboration.** R2 and R3 counted the same gap lines independently and agree (511 lines, 7,424 minutes, 83 returns;
median worker brief about 12.6k to 12.9k characters, R3's header).

## 2. What changes

| File | Change |
|---|---|
| `template/governance/kernel/templates/brief.md` | New: T-0, the envelope every launched session receives on stdin (where you work, KPI lines with `verify`, inputs, commands, forms that work, the commit form with the link lines, the return form). Search again once (DEC-1092), D5 rows 5, 6 and 10 |
| `template/governance/kernel/templates/ticket.md` | Replaced: T-1, front matter `name`, `version`, `role: any` (and the store fields `id: PROJ-0000`, `type: task`, `status: open` kept, so W1-30's template-ticket cases keep their premise), the skeleton as one fenced `yaml` block with `non_goals`, `{line, verify}` KPI lines, `reads`, `needs`, `waits_on`, `done_when` |
| `template/governance/kernel/templates/role-research.md`, `role-product-spec.md`, `role-test-designer.md`, `role-engineer.md`, `role-reviewer.md`, `role-lead.md`, `role-cto.md` | New: T-2 to T-8, from R3's Appendix, each within R3 §C's budget, with the link lines of LINK-INTEGRITY §5 and D5 rows 1 to 4 and 7 to 9; T-6 holds `JUDGEMENT.md`'s content as its Judgement section and the reversal line (DEC-1014) |
| `template/governance/kernel/templates/keys.yaml` | New: the key list the generator reads |
| `template/governance/kernel/templates/checkpoint.md`, `decision-record.md`, `decision-package.md`, `failure.md`, `lesson.md`, `research.md` | The link lines (fields and a comment); `research.md` gains "Decision it feeds" and "Stop rule" (R3-12) |
| `template/governance/kernel/templates/brief-engineer.md`, `brief-test-designer.md`, `brief-reviewer.md`, `brief-product-spec.md`, `brief-lead.md` | Each a one-line pointer to its replacement |
| `template/governance/kernel/roles/engineer.md` (and its `.rulesync/` sources) | Line 5: "to fulfil the spec and its KPIs" (DEC-957) |
| `template/governance/kernel/schemas/facts.schema.json` | New: the facts file's schema |
| `template/governance/kernel/schemas/ticket.schema.json` | Optional `non_goals`, `reads`, `needs`, `waits_on` (a string or `{ref, reason}`); a KPI line a string or `{line, verify}` |
| `template/governance/kernel/schemas/lesson.schema.json`, `failure.schema.json`, `research.schema.json` | Optional `sources`; research also optional `decisions` |
| `governance/project/facts.yaml` | New (project-owned): `paths`, `commands` (each with `run` and `check`), `dod` (six), `steps` (eight switches, on), `budgets`, `harness_allowed` |

**Round 2a (text, product-spec, DEC-1112 (3)):**

| File | Change |
|---|---|
| `template/governance/kernel/skills/test-design/SKILL.md` (1.0.0 → 1.1.0) | Kernel. "Read restriction": the designer may read the integrated code on `w2/integrate` and never this ticket's implementation (DEC-963, DEC-820 (c)); the ban on `src/` dropped (review F7; TPL-6 S3) |
| `template/governance/kernel/skills/orchestration/SKILL.md` (1.0.0 → 1.1.0) | Kernel. Lines 14, 29 and 61 point to the kernel templates (`brief.md` and the `role-*.md`) in place of the retired `brief-*.md` texts; "states each step in full" and "the standing sentences word for word" retired (review F6; DEC-1050, DEC-1052). K-4's two lines (84, 85) restated per DEC-820: reads open, four refusals, the held-out contents kept (DEC-820, DEC-525; K-4 approved by DEC-1052) |
| `template/governance/kernel/roles/orchestrator.md` | Kernel. Line 39: a lead is started from `brief.md` and `role-lead.md`, not `brief-lead.md` (review F6) |
| `template/governance/kernel/templates/checkpoint.md` | The example's ticket ids are the placeholder `{ID}` (a key in `keys.yaml`), not `DAEO-0000` |
| `template/.rulesync/skills/{discovery,retrieval,orchestration,test-design}/SKILL.md` | Byte copies of the kernel skills (discovery and retrieval had not been copied after their 1.1.0) |
| JUDGEMENT's rules (TPL-6 S4, kernel half) | Checked: only `role-reviewer.md` (T-6) carries them among the kernel templates; no change |

**Round 2b (text, product-spec, DEC-1112 (3); review `reviews/w2-128-r2a.md` F1, F2, F4 and the checkpoint link notice):**

| File | Change |
|---|---|
| `template/.rulesync/subagents/orchestrator.md` | Line 47-48: a lead is started from `brief.md` and `role-lead.md` (DEC-537, DEC-1050), the kernel role's line 39-40, not `brief-lead.md` (review F1). The repository's `.rulesync/subagents/orchestrator.md` is the ACT's |
| `template/governance/kernel/skills/orchestration/SKILL.md` (1.1.0 → 1.2.0) | Kernel (review F2). Line 55: "never two writing sessions in one tree" cites DEC-963 item 1, not the expired DEC-254; the commit-while-a-worker-runs half keeps DEC-537. Line 76: the per-round `gov checkpoint` record dropped as DEC-1057 (R-6) lifts it from DEC-511; a checkpoint written is a real one, never one only for the close (DEC-511, DEC-1057). Line 83: "or read from another session's folders" dropped; reads are open apart from DEC-820's four refusals (line 84) |
| `template/governance/kernel/skills/test-design/SKILL.md` (1.1.0 → 1.2.0) | Kernel (review F4). Line 13 (read rule) and line 17 (Inputs 1) cite CAP-38.c (independent test authorship), not CAP-38.b (governance test families) or DEC-136 (probe findings). "Writing acceptance tests" (lines 24 to 26) keeps CAP-38.b: round 2a's guard case allows no change there; a row for the next round |
| `template/governance/kernel/templates/checkpoint.md` | Line 7: `task: ''`, its comment naming the ticket's id `{ID}` to fill, so `gov links` reads no unknown id in the template (review F5's notice, from the template side) |
| `template/.rulesync/skills/{orchestration,test-design}/SKILL.md` | Byte copies of the kernel skills again |

Every existing record stays valid: `python3 -m gov.check.schema` validates 974 records with no finding after round 2a (2026-11-09). Round 1: 970 records with no finding after the change (fresh run, 2026-11-09, round 1 fixes).

## 3. The three options (DEC-105)

| Option | What it means here | Cost |
|---|---|---|
| **Apply now** (the owner's filing, DEC-1081 (2)) | The templates, schemas and facts land as in §2; round 2 builds `gov brief` and the launcher flag on them | This ticket's two rounds, its acceptance suite, one independent review |
| Defer | Keep the four layers and the hand-written briefs | The gap minutes and the contradictions of §1 continue |
| Re-baseline | Cut the brief text without templates | Refused by DEC-1050 (7): better guidance, not less |

## 4. Impact

| Area | Impact |
|---|---|
| Acceptance suites of other tickets | W1-35's S14 cases read the five `brief-*.md` texts word for word; TPL-1 S4 reduces them to pointers, so those cases enforce the superseded texts and need a test designer's revision under DEC-866 (`Rewrite-Reason:`). W1-42's case needs only the files to exist; they do |
| Generated copies | `.claude/agents/engineer.md` (line 5) and, in round 2, `.claude/templates/*.md`: installed by the owner's operator as an ACT (DEC-315, DEC-1081) |
| The guard, the launcher, the close | None in round 1, round 2a or round 2b |
| Generated skill copies (round 2a) | `.claude/skills/{orchestration,test-design,discovery,retrieval}/SKILL.md` and `.rulesync/skills/…`: the operator's ACT (`ACT-CLAUDE-COPIES-1`) |

## 5. CAP-33's steps

| Step | State |
|---|---|
| Evidence | §1 (R2, R3, LINK-INTEGRITY §5, D5-ROWS) |
| Corroboration | §1: R2 and R3 agree on the counts |
| Proposal | This record (round 1 draft) |
| Independent review | Done: READY for round 1, round 2a, round 2b, W2-152 (round 2) and W2-153 |
| Owner's approval | **Approved: "Templates approved at 1bf23a0b3e77"** (owner, chat, 2026-11-10; DEC-1116; TEMPLATES-APPROVAL-1's table) |
| Versioned promotion | Done: the kernel template set promoted as version 1.0.0 at `1bf23a0b3e77` (DEC-1116) |
| The `.claude/` copies | ACT-CLAUDE-COPIES-1 applied (`eb48fe2f`); ACT-CLAUDE-COPIES-2 queued for the operator agent (the owner's yes, 2026-11-10) |
