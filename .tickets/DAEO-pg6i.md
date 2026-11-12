---
id: DAEO-pg6i
status: open
deps: []
links: [DAEO-2bdu, DAEO-zmo4]
created: 2026-11-12T16:55:43Z
type: task
priority: 1
assignee: product-spec
external-ref: W2-88a
parent: DAEO-2bdu
tags: [wave-2, product-spec, adoption, memory, kernel-skill, standard]
wbs_id: W2-88a
title: 'W2-88a The adopt skill states Wave 0''s memory practice in order, and the Verify pass (W2-88''s and W2-174''s kernel skill text)'
class: specification
state_class: AUTHORITATIVE
role: product-spec
profile: STANDARD
depends_on: []
waits_on: []
allowed_paths:
- template/governance/kernel/skills/adopt/SKILL.md
- template/.rulesync/skills/adopt/SKILL.md
- .rulesync/skills/adopt/SKILL.md
# .claude/skills/adopt/SKILL.md out of the paths: generated from the kernel skill by the copies ACT after the owner's approval (DEC-315)
- docs/changes/W2-88a-CIT-P.md
- docs/research/W2-88-memory-practice.md  # the practice record the skill points to, refreshed to S17's order (from W2-88)
est_loc: 80
reads:
- .tickets/DAEO-2bdu.md
- .tickets/DAEO-zmo4.md
- docs/research/W2-88-memory-practice.md
- template/governance/kernel/skills/
needs: []
kpis:
  success:
  - 'S17 The Wave 0 order in the adopt skill: A9''s step in template/governance/kernel/skills/adopt/SKILL.md states the practice in order and points to the practice record. The order: assess and plan; census the stated links and build the graph from them; build the store with the standard (S10) and its refresh (S11); have the verdict set and the tuning set written (S13, S12); measure the tuning set and fix only the structure, never a named question, until its halves agree within 5 points; declare and measure the verdict set once (S14); record every method and figure. Verify: a string test on the skill for the steps in that order, and the skills check [DEC-1098 (1), DEC-1072 (2), DEC-1071 (1)-(3), DEC-1074 (4), CAP-33] [added, DEC-1099 (2); DEC-1098 (1)]'
  - line: "The adopt skill, in the kernel copy and the two generated-source copies, states the pass: when it runs (for a ticket about to launch, not for the whole tracker), who writes the clauses (a product-spec session), what checks them (the tool, the ticket's test designer, the auditor's sample), and that the owner approves the rule once [DEC-1130, DEC-1083]"
    verify: "tests/unit/adopt/test_w2_174_skill.py: the three files carry the section `Verify clauses for adopted tickets` with the four statements, and the three copies are equal in that section"
  - 'The CIT-P record (docs/changes/W2-88a-CIT-P.md) gives the kernel skill''s sha256 before and after, the lines added or removed, the independent review and the owner''s approval of the bytes before the merge; the two .rulesync copies equal the kernel copy in the changed sections Verify: the record holds both hashes and the review''s verdict; a diff of the three files shows the same changed sections [CAP-33, DEC-1116]'
  failure: []
non_goals:
- the adopt code (W2-88, W2-174) and the proofs (W2-88b); the .claude/ copy (the copies ACT)
done_when: [DOD-1, DOD-2, DOD-3, DOD-4, DOD-5, DOD-6]
sources: [DEC-1150, DEC-996, DEC-995, DEC-1098, DEC-1130, CAP-33]
acceptance_tests:
  path: tests/acceptance/W2-88a/
  author: independent-test-designer (MR-3); written before the text
track: A
---
# W2-88a The adopt skill's kernel text (a child of W2-88)

Filed by the owner's decision (DEC-1150 (1), package 1 (a), 2026-11-12), under DEC-996 (1)'s split list: W2-88 mixed three roles (DEC-995). This child holds the kernel skill text: W2-88's S17 (moved word for word) and W2-174's skill line (its S5, moved word for word, so the adopt skill is written once under one CIT-P). The two `test_w2_174_skill.py` and S17 string tests named in the moved lines are this ticket's acceptance tests, written by its test designer under `tests/acceptance/W2-88a/`. It can start now; the owner approves the skill's bytes before the merge (CAP-33).
