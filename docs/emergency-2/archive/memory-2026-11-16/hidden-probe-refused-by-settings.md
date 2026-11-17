---
name: hidden-probe-refused-by-settings
description: "a Read probe of memory-retrieval/hidden/ is refused by the permission-settings deny before the hook runs; it proves the wall, not the hook's rule"
metadata:
  node_type: memory
  type: project
  originSessionId: b7cdd573-fb34-40eb-a66c-d19cad4526cd
  modified: 2026-11-15T16:14:38.442Z
---

W2-15a's refused probe (2026-11-15 16:13:58 UTC, lead session, Read of a nonexistent file in
~/gov-os-eval/fixtures/evaluation/memory-retrieval/hidden/) returned "File is in a directory that is denied by your
permission settings." — the harness deny (ACT-PERMISSIONS-2's rule; also in the main tree's .claude/settings.local.json),
which decides before .claude/hooks/pretooluse.py.

**Why:** a probe meant to prove "the five-rule hook refuses it" only proves the settings layer when that deny is present.
**How to apply:** when a KPI needs the hook's own refusal shown, say which layer refused; a hook-only proof needs a
session without the settings deny (or the hook driven with a synthetic event). Related: [[act-in-progress-holds-operator]].
