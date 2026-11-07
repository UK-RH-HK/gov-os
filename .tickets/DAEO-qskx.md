---
id: DAEO-qskx
status: open
deps: []
links: [DAEO-t8mp, DAEO-rmhj]
created: 2026-11-07T19:01:42Z
type: task
priority: 2
assignee: product-spec
external-ref: W2-142
tags: [wave-2, skill, lite]
wbs_id: W2-142
title: 'Search again once in the kernel skills: the retrieval skill''s step 7 and the discovery skill''s line, after the practice is proven in use (DEC-1094 (2), SEARCH-AGAIN-PRACTICE §3.1-3.2)'
class: skill
state_class: AUTHORITATIVE
role: product-spec
depends_on: []
allowed_paths:
- template/governance/kernel/skills/retrieval/SKILL.md
- template/governance/kernel/skills/discovery/SKILL.md
- docs/changes/W2-142-evidence.md
kpis:
  success:
  - 'S1 The retrieval skill gains step 7, after step 6, with SEARCH-AGAIN-PRACTICE §2''s practice (the paragraph, the "does not answer" list in short, the cap of two searches), W2-138''s step-5 line kept, version 1.0.0 to 1.1.0, under the skills validator''s size budget. Verify: a string test for "search again once", "own, different words", "not found", "two searches", and the skills check [DEC-1094 (2), DEC-1092 (1)]'
  - 'S2 The discovery skill''s line 55 gains one sentence: search again once before routing a question to the owner as unanswered. Verify: a string test and the skills check [DEC-1094 (2)]'
  - 'S3 It lands at the lift''s re-pin ACT, with the generated .claude/ copies regenerated there (the retrieval skill''s copy is regenerated for W2-138 at the same ACT), and only after the project layer has been in use (CAP-33; DEC-1052''s fifth test): the adoption count''s first reading is in the evidence. Verify: the ACT''s record and the evidence [DEC-1094 (2), CAP-33]'
  failure:
  - 'Any change to a skill beyond the two named lines, or W2-138''s step-5 line lost.'
profile: LITE
sources:
- DEC-1094
- DEC-1092
- DEC-1085
- CAP-33
est_loc: 0
acceptance_tests:
  path: tests/acceptance/W2-142/
  author: independent-test-designer (MR-3), string tests on the two skills, before the product-spec change
track: B
list_rows: []
needs:
- template/governance/kernel/skills/retrieval/SKILL.md
waits_on: []
---
# W2-142 Search again once in the kernel skills

The owner's DEC-1094 (2), approving SEARCH-AGAIN-PRACTICE
(`governance/project/orchestration/packages/LIFT-1/SEARCH-AGAIN-PRACTICE.md`) as recommended: the project layer now
(EMG-common, LEAD-w2-common line 30, AUDITOR-common line 8, applied with DEC-1094), the kernel layer after it is proven
in use, through CAP-33. This ticket is the kernel layer's two skills (§3.1, §3.2); W2-128 carries T-0's and T-8's line
(its KPI line marked DEC-1094).

- **Patches:** the package's §3.1 and §3.2, exactly.
- **Timing:** tests first (string tests); lands at the lift's re-pin ACT.
- **Est.:** about 2 to 3 hours of agent time.

[DEC-1094]
