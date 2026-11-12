---
id: W2-152-CIT-P
type: change-impact-proposal
status: APPROVED
date: 2026-11-12
branch: w2/W2-152
base: b0bbd373f^1 (w2/integrate before the merge)
head: 09fc68645c0c (the code reviewed and merged)
ticket: DAEO-o5x1 (W2-152)
task: DAEO-o5x1
author: orchestrator (the CTO, written after the fact, DEC-1147; the form of W2-146's record, written by its ticket lead)
review: READY, round 2, independent auditor (governance/project/orchestration/reviews/w2-152-r1.md; docs/probes/DAEO-o5x1/PR-DAEO-o5x1.md)
approved: owner, 2026-11-12, after the fact ("W2-152 CIT-P approved at 09fc68645c0c, after the fact", DEC-1147 (1))
decisions_carried: [DEC-1088]
decisions_applied: [DEC-1088, DEC-1050, DEC-1147]
state_class: EVIDENCE
---

# W2-152: change-impact record (CIT-P) on the kernel's facts schema, written after the fact

**Written after the fact.** This change's kernel bytes were merged into `w2/integrate` by the CTO's merge `b0bbd373f`
(2026-11-09 23:07 UTC) before any CIT-P record or owner approval (CAP-33). Nothing in the merge path asked for an approval line
(DECIDED-NOT-DONE row 173). The owner found it through W2-152's resume of 2026-11-12, read the lines below and approved them after
the fact the same day (DEC-1147 (1)). This record states what was merged; it proposes nothing new.

## 1. What triggers the change

`gov brief` (W2-152) holds the ready check of DEC-1088 (3): a ticket created on or after a project's start date must declare
`reads:`, `needs:` and `waits_on:`; an older ticket is not refused for them. The start date is a project fact, so it lives in the
facts file (`governance/project/facts.yaml`, DEC-1050 TPL-2), whose kernel schema gains the key.

## 2. The kernel file: `template/governance/kernel/schemas/facts.schema.json`

| | sha256 |
|---|---|
| Before (`b0bbd373f^1`) | `be3e204355c0dd4c98cc584b72a1cef5eaa4733ca9a7feec8684b728026af7a6` |
| After (`b0bbd373f`, `09fc68645c0c`, and w2/integrate on 2026-11-12) | `3141d5da38d7a2a1dcf654f83354f4fc6f2ce16bb383c03d6a906e221bd6448c` |

15 lines added, 1 removed (`git diff b0bbd373f^1 b0bbd373f -- template/governance/kernel/schemas/facts.schema.json`):

```diff
@@ -3,7 +3,7 @@
   "title": "facts",
   "description": "The project facts file (governance/project/facts.yaml) the kernel templates are filled from (DEC-1050 TPL-2): named paths, named commands each with a check form, the Definition of Done (at most six lines, quoted by id), the step switches with the M3 match pattern of each, the prose budgets per template, and the commands the harness allows headless. A `paths` name upper-cased is a template key ({TREE} is paths.tree).",
   "type": "object",
-  "required": ["paths", "commands", "dod", "steps", "budgets", "harness_allowed"],
+  "required": ["paths", "commands", "dod", "steps", "budgets", "harness_allowed", "ready"],
   "additionalProperties": false,
   "properties": {
     "paths": {
@@ -68,6 +68,20 @@
       "description": "The commands the harness runs headless without asking (from the settings' allow list).",
       "type": "array",
       "items": { "type": "string", "minLength": 1 }
+    },
+    "ready": {
+      "description": "The ready check inside gov brief (W2-152, DEC-1088 (3)): a ticket created on or after `new_since` must declare reads:, needs: and waits_on:; an older ticket is not refused for them.",
+      "type": "object",
+      "required": ["new_since"],
+      "additionalProperties": false,
+      "properties": {
+        "new_since": {
+          "description": "An ISO date as a quoted string (\"2026-11-10\"): the day W2-152 lands.",
+          "type": "string",
+          "format": "date",
+          "pattern": "^[0-9]{4}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])$"
+        }
+      }
     }
   }
 }
```

Commits: `16d052d2f` (the `ready` property, 14 lines) and `09fc68645` (the fix round: `ready` added to `required`, review round 1's
F3: without the key the dependency-field check switched off silently).

## 3. What else changed in the same merge (product code and project files, not kernel)

`b0bbd373f` brought 34 files (2,561 lines added, 1 removed): `gov brief` (`src/gov/brief/__init__.py`, `build.py`, `command.py`);
`governance/project/facts.yaml` gaining `ready: new_since: "2026-11-10"` with a two-line comment; the acceptance suite
`tests/acceptance/W2-152/` (README, seven test files, support, fixtures); `tests/unit/brief/test_brief_build.py`;
`docs/changes/W2-152-evidence.md`.

## 4. The three options (DEC-105), as brought to the owner on 2026-11-12

- (a) Approve after the fact and write this record (chosen, DEC-1147 (1)).
- (b) Revert the 16 lines on w2/integrate: `gov brief` loses its required key; a fix round, and lead briefs refused until it lands.
- (c) Hold: W2-152 unclosed, and W2-174 and W2-27 behind it.

## 5. Impact

- This repository's facts file carries `ready.new_since: "2026-11-10"`; every ticket filed since must declare its three fields
  (W2-121b's brief was refused for it on 2026-11-12 until they were declared).
- An adopted repository has no facts file today (`gov adopt` writes none), so `gov brief` there refuses with BRIEF_FACTS_MISSING before
  it reads `ready`; that is a separate item with the owner (DEC-1147 (2)).
- Every brief built with `gov brief` since 11-09, and the 11-11 re-pin (DEC-1125 (3)), use this schema.

## 6. Verification and independent review

- Review: two rounds by an independent auditor (`governance/project/orchestration/reviews/w2-152-r1.md`); round 2 READY on
  `09fc68645c0c` (2026-11-09). Round 1 read the facts schema: S10 pass (`format: date` and the date pattern); F3 fixed in the fix round.
  The review judged the code against the KPI lines; it was not a CIT-P review.
- `gov accept W2-152`: 67/67 on the merged head `e25bdca86bc1` (2026-11-12 resume; `docs/probes/DAEO-o5x1/PR-DAEO-o5x1.md`).
- The owner's approval: DEC-1147 (1), after reading the lines in section 2.
