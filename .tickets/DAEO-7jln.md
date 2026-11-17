---
id: DAEO-7jln
wbs_id: W2-193
external-ref: W2-193
status: open
deps: []
links: []
created: 2026-11-16T15:51:18Z
type: task
priority: 2
assignee: Usain
parent: DAEO-sdxk
tags: [wave-2, close, adoption]
class: implementation
role: engineer
profile: STANDARD
state_class: AUTHORITATIVE
allowed_paths:
- src/gov/close/command.py
- src/gov/close/batch.py
- src/gov/close/select.py
- tests/unit/close/test_w2_193*
reads:
- src/gov/close/**
- drafts/w2-27-findings/PRODUCT-FINDINGS.md
needs: []
waits_on: []
est_loc: 150
kpis:
  success:
  - line: "S1 In a project whose suites collide (two folders with the same test module names or conftest.py, e.g. a legacy suite and its kit copy), gov close runs each colliding suite in its own pytest process, so no collection error or import collision comes from running them together [DEC-1203 (3), F-028]"
    verify: "tests/unit/close/test_w2_193_collide.py: a fixture project with two suites holding test_a.py and conftest.py each; the close's run collects and runs both with no ImportPathMismatch or collision error, each in a separate process"
  - line: "S2 A red's alone re-run uses a node id that pytest resolves in the process and folder the red came from, so no red is recorded as absent because its id could not be found [DEC-1203 (3), F-028]"
    verify: "tests/unit/close/test_w2_193_alone.py: a fixture red in a nested suite folder; its alone re-run resolves and runs it (no 'absent' type for a test that exists)"
  - line: "S3 When no green base exists (the base run collected zero tests or failed to run), the close records that and compares each red with the base run's own result for that node, never counting every red as caused by the change [DEC-1203 (3), F-024, F-028]"
    verify: "tests/unit/close/test_w2_193_base.py: a fixture whose base run is empty: the close names the missing baseline and attributes no red to the change without a base result"
  failure:
  - line: "F1 A project without colliding suites, or with a green base, closes differently than before"
    verify: "the existing close cases (tests/unit/close, tests/acceptance/W2-*close*) pass unchanged"
non_goals:
- "no change to accepted_reds or to scoped mode (W2-194)"
- "no change to the kernel schemas"
done_when: [DOD-1, DOD-2, DOD-3, DOD-4, DOD-5, DOD-6]
sources: [DEC-1203, DEC-1199, DEC-968, DEC-974]
acceptance_tests: {path: tests/acceptance/W2-193/}
---
# gov close's harness in an adopted repository (F-028)

# W2-193 gov close's harness in an adopted repository (F-028)

Filed 2026-11-16 by the CTO on the owner's word (DEC-1203 (3): "EXA-CLOSE (c); this also approves the product tickets for F-028 and F-030").

**Problem (EXAMIN, exa-g6db's close, reports 15c and 18; F-028, F-024).** In an adopted repository, gov close's scoped run put EXAMIN's legacy suite and its kit copy in one process (colliding module names and conftests), its alone re-runs used node ids pytest could not find (recorded as `absent`), and with no green base every red was attributed to the change (140 RED_CAUSED, of which 7 were the change's).

**Approach.** Colliding suites run in separate processes; alone re-runs carry the node id the red's own run used; an empty or failed base is named and compared per node. Evidence: `drafts/w2-27-findings/PRODUCT-FINDINGS.md` (F-024, F-028), EXAMIN's reports 15c and 18.
