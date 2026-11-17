---
name: no-timeout-wrap-on-closes
description: "never wrap close_build.py (or any test-running close/land) in `timeout 600` inside a background call; it killed W2-138's dry close after selection (rc 124, 11-16)"
metadata:
  node_type: memory
  type: feedback
  originSessionId: acd80751-ac8f-4230-9bae-15c678a54895
  modified: 2026-11-16T05:43:59.700Z
---

On 11-16 at 05:32 I ran `timeout 600 python3 close_build.py W2-138 --dry` in a background Bash call. The clone, rebuild and selection (255 targets) took about 2 minutes, then `timeout` killed it before any test ran (rc 124), and the run had to start again.

**Why:** a background call already has a 7200000 ms limit. An inner `timeout` sized for a foreground call cuts off the long part of the run.

**How to apply:** start test-running tools (close_build, land, gov accept, lead_verify) with run_in_background and the 7200000 ms timeout, with no `timeout N` around them. A `--dry` close runs the full tests too, so it costs as much as the real close; go straight to the real close, which stops before writing on any failure. Related: [[long-runs-background-timeout]].
