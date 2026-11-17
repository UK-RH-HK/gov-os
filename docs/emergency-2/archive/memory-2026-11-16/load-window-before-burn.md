---
name: load-window-before-burn
description: "never run a load generator (CPU burners for \"load 20 / 50+\" KPI runs) without the CTO's window — it shuts the resource gate for critical-path work"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 4bcdcab9-03c1-4587-8f57-8f34b1057b48
  modified: 2026-11-15T02:09:26.745Z
---

A KPI that asks for runs "at a load of about 20 and at 50 or more" needs a load window from the CTO before any burner starts. W2-111's lead (2026-11-15 01:10-02:08Z) ran burn.py at loads 20-58; the machine's resource gate shut (load ~45 vs nproc 20) and W2-88, on EXAMIN's release critical path, was refused workers. The CTO stopped it (DEC-1157: critical-path work never waits) and moved the loaded runs to after the re-pin.

**Why:** the gate is shared; a lead cannot see which other tickets are on the critical path.

**How to apply:** ask the CTO (SendMessage) for a load window and say how long; until then do only quiet runs. Keep burners in their own process group with a self-ending limit, and stop them by -pgid via proc.sh. Related: [[gate-refusal-is-a-wait]], [[waits-by-pid-only]].
