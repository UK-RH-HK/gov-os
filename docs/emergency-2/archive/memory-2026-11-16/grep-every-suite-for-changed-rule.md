---
name: grep-every-suite-for-changed-rule
description: "Before a TD brief that changes a rule other suites assert (e.g. an empty allowlist), grep all of tests/ for that assertion and name every case; the ticket's list may be short"
metadata:
  node_type: memory
  type: feedback
  originSessionId: cd5b16a2-7b43-44f1-b9e6-0e8bb2de8d1d
  modified: 2026-11-16T16:58:19.473Z
---

When a ticket amends a rule (W2-186: workers' `allowedDomains` no longer empty, DEC-1168 (1)), grep the whole of `tests/` (acceptance and unit) for the old assertion before writing the test designer's brief. The ticket named only W2-56/W2-112/W2-145; W1-33, W1-46 (x3), W1-28 (x2) acceptance and unit test_w1_28.py:89 also assert `allowedDomains == []` and were left out of td-1 (2026-11-16).

**Why:** the missed cases go red only after the build, in lead_verify, and then need a CTO path case (DEC-1156 (7)) mid-build instead of one TD batch.
**How to apply:** `grep -rn "<old value or key>" tests/` at brief time; list each hit in the brief's revisions section, or raise the path case to the CTO in the tests run's return. Related: [[cto-fixes-path-cases]].
