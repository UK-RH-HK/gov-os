---
name: check-map-with-parse-map
description: "before briefing a gov accept map fix, run the product's parse_map and line_names on the README to find every refused row, not only the first one named"
metadata:
  node_type: memory
  type: feedback
  originSessionId: acd80751-ac8f-4230-9bae-15c678a54895
  modified: 2026-11-14T23:31:45.148Z
---

On 2026-11-14 I briefed W2-188's README fix naming only the self-check row. `parse_map` also refused all eight KPI cells (each started with a backticked name) and a cell holding "S10" outside a code span. The lead found both and fixed them beyond my brief's "no other row" line.

**Why:** a brief that names only part of the cause makes the lead choose between going over the brief and returning PACKAGES, which costs a round.

**How to apply:** for an `ACCEPT_MAP_UNREADABLE` refusal, run `from gov.accept.runner import parse_map` (and `line_names`) on the README first and list every refused row in the brief. A KPI cell starts with the bare line name; any `S<n>`/`F<n>` inside it goes in a code span. Related: [[check-before-ready-line]].
