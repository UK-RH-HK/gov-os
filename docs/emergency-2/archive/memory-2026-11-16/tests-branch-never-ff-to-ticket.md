---
name: tests-branch-never-ff-to-ticket
description: "never fast-forward the -tests branch to the ticket branch before a test designer revision: it brings the engineer's src into the TD's tree (DEC-820)"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 5fb98fa0-0315-4b34-89d8-c3ea57b1a7b1
  modified: 2026-11-15T18:11:31.241Z
---

2026-11-15 18:13 (W2-88 run 9): to give td-20 the merged head I ran `git -C W2-88-tests merge --ff-only w2/W2-88`; that put eng-16's `src` (the counterpart's work) into the test designer's tree. Undone at once with a reset to the TD's own commit (nothing lost).

**Why:** DEC-820 refuses a test designer the counterpart's work on the same ticket; the tests tree must hold only the base `src` plus the tests.

**How to apply:** a follow-up test-designer batch works on the -tests branch at its own last commit (the merged tests are already there); give it failing output only. Merge the tests into the ticket branch, never the ticket branch into the tests branch. Related: [[engineer-brief-no-acceptance-code]].
