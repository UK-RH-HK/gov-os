---
name: engineer-brief-no-acceptance-code
description: "An engineer's brief never tells it to read the ticket's acceptance-test code; give the failing output (names, messages, assertion lines) only"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 84594ce6-4ab1-4134-9546-6630fe3b6816
  modified: 2026-11-15T16:54:43.181Z
---

W2-94 en-3 (2026-11-15 16:50, as ticket lead): my brief said "Read: ... the red cases' code in tests/acceptance/W2-94/...". The engineer role forbids reading its ticket's acceptance-test code; the engineer followed the role and worked from the failure output alone.

**Why:** the test designer's independence (MR-3): the implementer builds to the interface, not to the tests' code. The template's own rule is "a fresh implementer given the failing output only".

**How to apply:** in an engineer's brief, paste the failing output (case ids, assertion lines and messages) and the interface; never list `tests/acceptance/<W2>/` files under "Read". Also check pinned return shapes (e.g. a dict that must equal exactly N keys) before suggesting a data shape in a brief. Related: [[pytest-through-heavy-slot]].
