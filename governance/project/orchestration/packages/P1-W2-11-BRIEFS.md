---
status: "ANSWERED (DEC-1137, option (c) and the small ticket)"
---
# P1-W2-11-BRIEFS: W2-11's brief KPIs name five templates W2-128 retired (DEC-105: apply now, defer or re-baseline)

**(1) Context.** W2-11 (`DAEO-k7hz`, STANDARD, kernel; "agents know what to do": the orchestration, test-design and QA
skills and the five brief templates) is the long pole of batch 1 (a 4-6 h resume) and gates W2-98, W2-120, W2-52 and W2-113,
on EXAMIN's path (W2-27's closure). Round 1 is DONE and unmerged (147 passed, 11-01). Since then W2-128 (TPL-1, DEC-1050,
templates 1.0.0 approved by DEC-1116) replaced the five `template/governance/kernel/templates/brief-*.md` files with one-line
pointers ("Replaced by role-<x>.md (the role) and brief.md (the envelope)"), and W2-152/W2-153 built `gov brief` and the
role templates on them. Full analysis: `.gov-runtime/scratch/orchestrator/drafts/w2-11/RESOLUTION.md` (§1 the 20
conflicted files, §4 this decision, §5-6 the skills' merge rules).

**(2) What happened.** Merging `w2/integrate` into `w2/W2-11` conflicts in 20 files (checked read-only, `git merge-tree`):
group A, one W1-35 acceptance file (solved: a test designer's pre-merge commit, running now, ~10 min); group B, the five
briefs (W2-11's text against integrate's pointers); groups C and D, 14 skill files and two generated copies (a product-spec
merge, mechanical per hunk, §5-6). Group B is the only part that needs you: taking integrate's pointers drops W2-11's side of
all five files, which a lead may not do (DEC-750, DEC-754), and W2-11's success lines on the briefs (and their cases) then
name files that carry no text.

**(3) Why it matters.** W2-11 cannot merge, re-verify and close until group B is decided, and four tickets on EXAMIN's path
wait on it. A merge that silently drops the ticket's side would close W2-11 on KPIs it no longer meets.

**(4) The options** (the helper's costing, `RESOLUTION.md` §4):
- **(a) Apply now:** take the pointers; product-spec re-homes the rules W2-11 still wants into `brief.md` and the
  `role-*.md` templates; a test designer revises W2-11's brief cases to follow the retired files (W1-35's pattern). Cost:
  about +2-3 h (two workers, one review); touches the approved templates (DEC-1116), so a template delta and its review.
- **(b) Defer:** land W2-11's skills and the rest now with the pointers taken; its brief lines become open rows for a
  follow-up ticket. Cost: merge about 1 h less; W2-11 closes with a named gap; risk: the brief rules W2-11 added live nowhere
  until the follow-up.
- **(c) Re-baseline:** you re-baseline W2-11's brief KPIs to what TPL-1 left (the skills, `skill.md`, the orchestration,
  test-design and QA-review skills, the audit's DEC-430 wording); the CTO edits the ticket under your decision; the five
  pointers stay. Cost: the least (a ticket edit, the brief cases retired by a designer); plus one small new ticket so the
  role templates carry Policy 2's four refusals, DEC-861's record rule and the two-refusal stop (live rules the templates
  lack today).

**(5) Recommendation:** **(c), with the one small ticket from (a)**, confidence medium. Classification of the findings:
ordinary work yes (a lead merging integrate hits it); consequence other (no fail-open; the risk is a close on stale KPIs).

**(6) What it blocks and what waiting costs.** It blocks W2-11's merge, its 4-6 h resume and close, and so W2-98, W2-120,
W2-52 and W2-113. Group A (the designer, running) and the skills' merge rules (C, D) go on meanwhile. Each day's wait
pushes those four tickets a day; EXAMIN's copy (about 11-16) has roughly a day's slack on this path.

Your answer: (a), (b) or (c) (and the small ticket yes or no).
