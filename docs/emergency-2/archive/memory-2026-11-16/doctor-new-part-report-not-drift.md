---
name: doctor-new-part-report-not-drift
description: "a new gov doctor part that names a gap a fresh copier project has must use status \"report\", not \"drift\" — W1-39's fresh-project doctor cases need healthy"
metadata:
  node_type: memory
  type: feedback
  originSessionId: fd9d7333-b642-4d28-8914-1cbc27639e44
  modified: 2026-11-16T01:02:04.976Z
---

A new `gov doctor` part whose gap exists in a freshly copied project (before `gov adapters generate`) must report with status `report` (names it, health unchanged), not `drift`/`fail`: W1-39's acceptance (`test_doctor_passes_on_a_freshly_created_project`, MINIMAL level, drift MATCH) needs doctor healthy there. `unmeasured` also downgrades ADOPTED_HEALTHY (`_check_adoption_level`).

**Why:** W2-153 en-1 (2026-11-16) briefed `drift` for missing template copies; lead_verify went red on 3 W1-39 cases; en-2 was needed.

**How to apply:** before briefing a doctor status, grep tests/acceptance for doctor-healthy assertions on fresh projects (W1-39, W1-27) and pick the status they allow. See [[lesson-to-memory-at-once]].
