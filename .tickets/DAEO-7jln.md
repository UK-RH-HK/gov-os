---
id: DAEO-7jln
wbs_id: W2-193
external-ref: W2-193
status: in_progress
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
- src/gov/close/attribution.py
- tests/unit/close/test_w2_193*
- tests/unit/close/test_w2_115*
reads:
- src/gov/close/**
- drafts/w2-27-findings/PRODUCT-FINDINGS.md
needs: []
waits_on: []
est_loc: 250
kpis:
  success:
  - line: "S1 In a project whose selected suites collide (two folders that are not packages holding a module of the same name, or a test module that imports conftest by name while another selected folder also holds a conftest.py, e.g. a legacy suite and its kit copy), gov close runs each colliding suite in its own pytest process, so no collection error or import collision comes from running them together, and every test of each suite is collected and run [DEC-1203 (3), F-028]"
    verify: "tests/acceptance/W2-193/ (README map, S1): a planted project with a legacy suite, its kit copy and the ticket's own suite, each with a conftest.py the tests import by name and same-named test modules; the scoped close's runs hold no collection error and no ImportError, each planted test ran, and the colliding suites ran in different processes"
  - line: "S2 A red's alone re-run uses a node id pytest resolves in the clone: a collection error is re-run as its module file, a test as its own node id; no red whose test exists is judged absent because its id could not be found [DEC-1203 (3), F-028]"
    verify: "tests/acceptance/W2-193/ (S2): a planted module that fails to import and a failing test in a nested suite folder; each red's alone runs (with the change and at the base) run it, and the record's reason for neither says absent"
  - line: "S3 With no --base and no green record on HEAD's line, the scoped close judges each red against the head without the change taken from git: the first parent of the ticket's oldest own commit; the close record names that commit under base and says where it came from under base_from (given, green_record or ticket); a red already red there with the same failure type is not the change's [EMERGENCY-2 6.1 (close against the base by default), DEC-1203 (3), F-024, F-028; supersedes DEC-1150 (2)'s no-fallback rule]"
    verify: "tests/acceptance/W2-193/ (S3): a planted project with no green record and a red red at the parent of the ticket's oldest own commit: the close passes, the record names base and base_from ticket and marks the red not caused; a red the change brings (green at that parent) still refuses RED_CAUSED"
  - line: "S4 When a red cannot be judged by its alone runs (absent or unknown on either side), the close runs the selection at the base, in the same process layout, and judges the red by that run's result for its node: red there with the same failure type is a base red; green or not collected there is the change's; when the base run collected zero tests or did not complete, the close refuses BASELINE_MISSING naming the base commit and those reds, never RED_CAUSED for them; the record's base_run says whether it ran, its counts and whether it completed [DEC-1203 (3), F-024, F-028]"
    verify: "tests/acceptance/W2-193/ (S4): a planted red whose alone runs cannot address it, red at the base run: not caused; green there: RED_CAUSED; a base where the selection collects nothing: BASELINE_MISSING naming the base, no RED_CAUSED"
  - line: "S5 The exa-g6db case: a scoped close in a project with no green record, whose base already has reds in a legacy suite and its colliding kit copy, closes (exit 0, ticket closed, close record written) when the change adds no red, every base red recorded as not caused [DEC-1203 (3), F-028, F-030]"
    verify: "tests/acceptance/W2-193/ (S5): the planted exa-g6db project; gov close <ticket> --json exits 0 and its record lists the base reds caused: false"
  - line: "S6 A base red that accepted_reds does not cover opens no repair ticket: the scoped close (and gov queue's close) proceeds, creates no file in .tickets/, and its close record lists each base red it saw, by test id, failure type and a reason that says it was red at the base, with repair_ticket null [EMERGENCY-2 4.2, CAP-31; a fix in the records of W2-115 and W2-193]"
    verify: "tests/acceptance/W2-193/ (S6): the planted exa-g6db project with base reds no accepted_reds entry covers: gov close <ticket> --json exits 0, the ticket is closed, .tickets/ holds no new file, and the close record's reds list every base red with caused false, red at the base in its reason and repair_ticket null; a red the change brings still refuses RED_CAUSED"
  - line: "S7 gov close does not require a review record: a FULL ticket with no probe record under docs/probes/<ticket>/ closes (the scoped close and the batch run) as a STANDARD ticket does, the record's review verdict READY with no record named; where a review did happen, READY stays computed by code from its verdict block (a FINDING_BLOCKS, VERDICT_NOT_REVIEWER or VERDICT_MALFORMED block still refuses) [EMERGENCY-2 3.6; audit 1]"
    verify: "tests/acceptance/W2-193/ (S7): a planted FULL ticket with no probe record: gov close <ticket> --json exits 0 and the close record's review is READY with record null (no VERDICT_MALFORMED); the same ticket with a probe record whose committed verdict block fails a KPI line is refused FINDING_BLOCKS"
  failure:
  - line: "F1 A project without colliding suites, or with a green base, closes differently than before; or a red the change brings is excused"
    verify: "the existing close cases (tests/unit/close, tests/acceptance of the close: W2-115, W2-66, W2-68, W2-150 and the rest importing gov.close) pass, save the cases S3 changes, rewritten by the test designer with a Rewrite-Reason; tests/acceptance/W2-193/ (F1): a red green at the base still refuses RED_CAUSED in each new route"
non_goals:
- "no change to accepted_reds or to the short --base (W2-194)"
- "no change to the strict close or the kernel schemas"
done_when: [DOD-1, DOD-2, DOD-3, DOD-4, DOD-5, DOD-6]
sources: [DEC-1203, DEC-1199, DEC-968, DEC-974]
acceptance_tests: {path: tests/acceptance/W2-193/}
---
# gov close's harness in an adopted repository (F-028)

# W2-193 gov close's harness in an adopted repository (F-028)

Filed 2026-11-16 by the CTO on the owner's word (DEC-1203 (3): "EXA-CLOSE (c); this also approves the product tickets for F-028 and F-030").

**Problem (EXAMIN, exa-g6db's close, reports 15c and 18; F-028, F-024).** In an adopted repository, gov close's scoped run put EXAMIN's legacy suite and its kit copy in one process (colliding module names and conftests), its alone re-runs used node ids pytest could not find (recorded as `absent`), and with no green base every red was attributed to the change (140 RED_CAUSED, of which 7 were the change's).

**Approach.** Colliding suites run in separate processes; alone re-runs carry the node id the red's own run used; an empty or failed base is named and compared per node. Evidence: `drafts/w2-27-findings/PRODUCT-FINDINGS.md` (F-024, F-028), EXAMIN's reports 15c and 18.

**Fix, 2026-11-18 (EMERGENCY-2 4.2, 3.6; S6, S7; branch e2/close-e2).** `gov close` no longer opens a repair ticket for a base red `accepted_reds` does not cover (W2-115 S5, CAP-31): a known bug is a fix recorded in its owning ticket's record, not a ticket, so the close record lists the base reds it saw and the close proceeds. It no longer refuses a FULL ticket for lacking a review record (W2-115 S11): no ticket gets a reviewer; where a probe record with a verdict block exists, READY is still computed by code. W2-115's cases that asserted the repair ticket or the missing-review refusal are revised with a Rewrite-Reason line.
