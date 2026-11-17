---
name: gate-refusal-is-a-wait
description: "A resource gate's refusal (memory, CPU, disk, heavy slot) is a wait, not a two-refusal-rule refusal; relaunch when it opens without asking"
metadata:
  node_type: memory
  type: feedback
  originSessionId: b2f0511f-891b-4874-8930-6d34ca5972ea
  modified: 2026-11-12T14:37:29.692Z
---

A resource gate's refusal (memory, CPU, disk, a heavy slot) is a **wait**, not a refusal under the two-refusal rule. Relaunch when the gate opens, without asking the owner. The two-refusal rule (DEC-1142 (9)) covers **permission** refusals only: the guard, the sandbox, a hook.

**Why:** the owner's standing reading, 2026-11-12 (P1-I (a), DEC-1146). My P1-D reviewer and W2-152's re-probe were refused twice each by the memory gate, and both stopped under the two-refusal rule.

**How to apply:** after a LAUNCH_REFUSED from the resource gate, wait for the heavy jobs to finish (wait by pid only, see [[waits-by-pid-only]]), then relaunch. Put this reading in lead briefs so leads don't stop on a gate refusal either. A guard, sandbox or hook refusal twice still means stop and say so.
