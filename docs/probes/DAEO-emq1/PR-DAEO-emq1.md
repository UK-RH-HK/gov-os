---
type: probe
task: DAEO-emq1
round: 3
reviewer_session: b652f762-603f-4a46-ad18-393d26dd6530
implementer_session: 83bbdb92-7c96-4756-99e6-cc563c0e782a (eng-5), 221d1199-a8e5-45a0-ab74-10a0925d3d6c (eng-6); round 1's f12efad7-fc16-481c-a9f1-c8b7f093f989, 4a29722c-bd73-421e-b2b8-60a994fb5030, 68e7b7a7-425e-44dd-bfdd-f794eb1effbc
reviewer_wrote_nothing: true
commissioned_by: orchestrator
judged_by: independent-auditor
judgement: pass
probed_commit: ea6dc2c1472723a3f9b50cc4f95420ebcb3e5415
decisions_applied: DEC-1150, DEC-1152, DEC-1010, DEC-802, DEC-988, DEC-989
---

# Probe record: W2-115 (DAEO-emq1), the narrow check of P1-K (a)'s fix (the owner's P1-M (a), DEC-1152 (3)): PASS

A fresh Independent Auditor session (`b652f762-603f-4a46-ad18-393d26dd6530`, claude-opus-5-5, effort high, read-only, class C3) checked only the fix that rode
run 5's resume after review round 2's FAIL on R2-1 (round 2's record: `PR-DAEO-emq1-round-2.md`). The owner allowed this one
narrow third look so the queue has a passing record (P1-M (a)); it is limited to the fix. The reviewer's blocks below are copied
unchanged from its return; the CTO commits this record because the reviewer is launched read-only.

# W2-115 (DAEO-emq1): narrow check of P1-K (a)'s fix (P1-M (a), 2026-11-12)

task: DAEO-emq1
decisions: [DEC-1150, DEC-802, DEC-1010, DEC-801, DEC-808, DEC-988, DEC-989, DEC-1146, DEC-1073]
head: ea6dc2c14727
reviewer: independent-auditor (fresh, read-only; launch sandbox)

## Checks
1. **The `src/` change since f39289d3a379:** inside `src/gov/close/` only. In `select.py`, `head_without_change` returns the green base when it is an ancestor of HEAD, else None, and its caller no longer passes the oldest own commit's parent. `attribution.py` and `command.py` change only the wording of a reason and of the `--base` help (FC-2). The merge 8e66a9bd7 brought only integrate's files: its 9 src files are byte-identical to 486bc0fb6 and disjoint from W2-115's 6.
2. **R2-1 is closed for the planted case.** td-5's case passes. Rebuilt independently (no record, an untrailered commit breaks the widget's test, trailered work follows): RED_CAUSED, exit 3, the ticket stays open, and the reason says there is no green base on HEAD's line. A red that predates the ticket, with no green record, also refuses (the fail-closed side). With a green base that is an ancestor, the same slip is judged on that base and refused (no regression). Not closed: a slip whose broken test the ticket's own paths do not reach (FC-1, out of scope).
3. **The test revisions:** each rewrite carries `Rewrite-Reason: DEC-1150 (2)` and changes only what P1-K (a) requires. R2-4's guards only add cases (FC-3). R2-5's `-I` fix is one line in the research doc. `gov accept W2-115` (heavy_slot, this head's src): 88 passed, 0 failed; outcome fail, exit 3, only because S12 maps no tests (round 2's S12-deferred, P4). The `src/gov/close/` unit tests: 157 passed, 0 failed.
4. **S1-S3 and S5-S7:** no test file and no code on their paths changed. gov accept: 9/9, 7/7, 1/1, 2/2, 12/12, 15/15.

## Findings
- **FC-1 | S2 (out) | src/gov/close/select.py:680.**
  - What was done: no green record; an untrailered commit breaks the gadget's test; trailered work changes only the widget.
  - What happened: the gadget's test is never selected; the close exits 0 and the ticket closes.
  - What should happen: if R2-1 covers every untrailered commit, the close should refuse.
  - Cause: with no green base the change is only the ticket's own commits, the design stated at select.py:677-678. The line is unchanged since f39289d3a379 (line 679), so the fix did not cause it.
  - Ordinary work: yes, because it has R2-1's premise (a new project with no green record, a forgotten trailer) on a commit touching another module.
  - Consequence: fails open.
  - Reversed by: an owner ruling that check 2's wording covers every untrailered commit (then scope in, and the check fails). Shown harmless by: the ticket's S2 line or an owner decision confirming "own commits only", or evidence that the queue or the nightly runs the gadget's tests before the land.
- **FC-2 | fix (in) | attribution.py:392, command.py:127.** Two strings change beside select.py; wording only. Ordinary work: no, because no behaviour changes. Consequence: other. Reversed by: a behaviour change in either file (there is none).
- **FC-3 | fix (in) | 4f8897e00.** No Rewrite-Reason on R2-4's commit; it only adds cases, and the test-map argument it threads through the helpers defaults to the old map. Ordinary work: no, because nothing existing was rewritten. Consequence: other. Reversed by: a rule requiring a Rewrite-Reason for additive changes.
- **FC-4 | environment (out) | the installed pin gov-os/pin-797495bdfc70.**
  - What happens: the pinned `gov accept` strips PYTHONUSERBASE (it predates W2-177), so under an empty HOME it reports crash with 0 tests run.
  - This head's own runner works.
  - Ordinary work: yes, because every sandboxed worker following the common brief hits it.
  - Consequence: other (fails closed).
  - Reversed by: a rebuilt pin that includes W2-177's runner.

## Probed and found sound
- With no green base or a base off HEAD's line, every red counts as the change's.
- The nightly record cannot stand in without a base.
- A green base that is an ancestor still excuses only reds that are red there too.
- The unit and acceptance revisions match the decision.
- The tree is clean at the end.

## Judgement
Classification: FC-1 is out of scope, ordinary work yes, fails open (a row for the owner). FC-2 and FC-3 are in scope, ordinary work no, other. FC-4 is out of scope, ordinary work yes, other. Nothing blocks under DEC-1010 within this check's scope, so the verdict is pass. FC-1 should reach the owner before the land, next to the EXAMIN first-green-base item.

```verdict
{"kpis": [{"kpi": "w2-115-fix-check", "verdict": "pass", "findings": [{"id": "FC-1", "scope": "out", "ordinary_work": "yes", "consequence": "fails open"}, {"id": "FC-2", "scope": "in", "ordinary_work": "no", "consequence": "other"}, {"id": "FC-3", "scope": "in", "ordinary_work": "no", "consequence": "other"}, {"id": "FC-4", "scope": "out", "ordinary_work": "yes", "consequence": "other"}]}]}
```
