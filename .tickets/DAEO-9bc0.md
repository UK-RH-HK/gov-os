---
id: DAEO-9bc0
status: closed
deps: [DAEO-k7hz]
links: [DAEO-k7hz]
created: 2026-11-02T00:18:23Z
type: task
priority: 1
assignee: product-spec
external-ref: W2-11b
tags: [wave-2, skill, standard]
wbs_id: W2-11b
title: 'The orchestration skill''s and the reviewer template''s seven lines that W2-11 landed without (SMART-WORK-3, SMART-WORK-4 lines 4, 6, 9, 10, SMART-WORK-5 B and C)'
class: skill
state_class: AUTHORITATIVE
role: product-spec
depends_on:
- DAEO-k7hz
allowed_paths:
- template/governance/kernel/templates/brief-*.md
- template/governance/kernel/skills/orchestration/**
- template/governance/kernel/skills/qa-review/**
- .claude/skills/orchestration/**
- .claude/skills/qa-review/**
- .rulesync/skills/orchestration/**
- .rulesync/skills/qa-review/**
- template/.rulesync/skills/orchestration/**
- template/.rulesync/skills/qa-review/**
- docs/changes/W2-11b-CIT-P.md
kpis:
  success:
  - 'The reviewer''s brief template requires the structured verdict block per KPI (scope, ordinary work, consequence per finding) and states the two questions word for word; the qa-review skill states the moderator''s triage, the blocking rule and the two-round cap, with one scenario each [DEC-1010 item 1, SMART-WORK-3]'
  - 'The reviewer states, per finding, what evidence would reverse it [DEC-1014, SMART-WORK-4 line 4]'
  - 'The orchestration skill: the status block''s counts (leads, queue, inbox, merged, closed, pings) are generated from files; a typed count is a slip [DEC-1014, SMART-WORK-4 line 6]'
  - 'Each standing rule in the orchestration skill names its mechanism, or says "prose only" with the reason [DEC-1014, SMART-WORK-4 line 9]'
  - 'The orchestration skill: the resume block comes first and the checkpoint stays under a set token budget; over it, the stop hook names it [DEC-1014, SMART-WORK-4 line 10]'
  - 'Delegation does not count the recommendation and the proposer''s agreement as corroboration on a decision that touches verification; that needs an independent reviewer''s record [DEC-1014 item 1, row 4, SMART-WORK-5 B]'
  - 'The daily document gives the week''s net ticket growth (filed minus closed, counted from the tickets) and the share of new tickets that fix the machinery; when net growth passes a configured share of the remaining plan in a week (default 5 %), it goes to the owner as one re-plan package with DEC-105''s three options, not as single P1s [DEC-1014 item 1, row 2, SMART-WORK-5 C]'
  failure:
  - 'A skill or template that still teaches the old rule (agreement counted as corroboration; a typed count; a rule with neither a mechanism nor "prose only").'
  - 'A copy (.claude/, .rulesync/, template/.rulesync/) that differs from its kernel source.'
profile: STANDARD
sources:
- DEC-1022
- DEC-1010
- DEC-1014
- DEC-1015
- DEC-105
est_loc: 120
acceptance_tests:
  path: tests/acceptance/W2-11b/
  author: independent-test-designer (MR-3)
track: A
list_rows: []
---
# W2-11b The orchestration skill's and the reviewer template's seven lines

The owner's DEC-1022 item 3 (P-W2-11-LINES (a)): seven approved KPI lines meant for W2-11 (SMART-WORK-3's reviewer
template and qa-review line; SMART-WORK-4 lines 4, 6, 9 and 10; SMART-WORK-5 B and C) could not ride in W2-11's round,
which landed without them. This ticket carries them, word for word. It starts once W2-11 (`DAEO-k7hz`) closes. If
W2-11 goes back for another round instead, the seven lines ride along in that round and this ticket is withdrawn.
SMART-WORK-5 B fixes a product defect: the kernel orchestration skill counts the recommendation's and the proposer's
agreement as corroboration (`template/governance/kernel/skills/orchestration/SKILL.md`).

**D9-FATES (DEC-1083):** Merged into W2-128 by DEC-1083. S1, F1 and F2 fold into W2-128's TPL-1 S3 and TPL-4 (no new line); S2 moved to W2-128 as the reviewer template's line; S3 to S7 lifted.
