---
name: long-runs-background-timeout
description: start gov accept / heavy-slot runs with run_in_background and a 7200000 ms timeout; a foreground call that times out is moved to background and killed at 10 min
metadata:
  node_type: memory
  type: feedback
  originSessionId: f8e3c2dc-e46f-45c5-8f6a-2c2888788652
  modified: 2026-11-16T07:31:59.604Z
---

Start any run that may wait on the heavy slot (gov accept, lead_verify, rebuild_slot) as a Bash call with `run_in_background: true` and `timeout: 7200000`, writing its own exit file; then wait on that file with wait_for.sh.

**Why:** on 2026-11-13 (W2-88 run 5) a foreground `gov accept` hit the 600 s limit while it waited for a heavy slot. The harness moved it to the background and killed it at its 10-minute background limit, so it had to be started again (about 20 min lost).

Repeated 2026-11-16 (W2-60b lead): a lead's own ad-hoc `heavy_slot.sh python3 -m pytest <one folder>` for failure reasons was killed the same way; this covers ANY heavy_slot pytest, even a one-folder run.

**How to apply:** the accept-N.sh / verify scripts already write their exit files, so start them in the background from the beginning. Related: [[pytest-through-heavy-slot]], [[gate-refusal-is-a-wait]].
