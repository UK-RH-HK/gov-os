---
name: accept-map-no-caseless-row
description: "a README map row with no case fails gov accept for ever; a git-diff F line (paths) goes in prose under the table, never a row"
metadata:
  node_type: memory
  type: feedback
  originSessionId: c7e8ceec-9a58-4522-8bde-e26ac89bcc18
  modified: 2026-11-16T15:59:53.214Z
---

`gov accept` (src/gov/accept/runner.py, the line loop after `missing = ...`) passes a mapped KPI line only when one of its cases passed; a row "checked by the lead, no case" is mapped with zero cases and is "fail" for ever, so the build run could never go green. W2-156 td-1 (2026-11-16): my brief told the test designer "write no case for F4; the README names it", and it put F4 as a table row; td-2 had to move it out.

**Why:** a lead brief defect cost one extra test-designer launch (only a test designer may edit tests/acceptance/).

**How to apply:** in every td brief, for a line checked outside the suite (the paths line F4, `git diff --name-only`), say: "keep it OUT of the map table: one prose line below it (W2-160 README line 64's form)". Check the README's map with a red `gov accept` before writing TESTS-READY: every line must have at least one case. Related: [[engineer-brief-no-acceptance-code]].
