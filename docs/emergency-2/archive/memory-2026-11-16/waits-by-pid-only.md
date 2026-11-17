---
name: waits-by-pid-only
description: "Every wait and stop by process id or group through tools/proc.sh, never a name match (L-0075, DEC-1073 (4))"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 33b3628c-7145-4e49-bfd8-2cfd894e92c4
  modified: 2026-11-16T06:46:44.759Z
---

Every wait and every stop uses process ids or process groups, never `pgrep -f`/`pkill` or any name match. The shared
helper is `.gov-runtime/scratch/orchestrator/tools/proc.sh`:
- `wait --max <s> <pid|-pgid>`: it is always bounded and exits 124 at the limit;
- `stop --grace <s>`: SIGTERM, then SIGKILL;
- `pgid <pid>`.

To chain one job after another, capture the first job's pid (or start both in one script) and wait on that pid.

**Why:** on 2026-11-04 a waiter ran `pgrep -f "measure_m.sh"`. Its own command line held that text, so it never
fired, and the GPU sat idle for about 20 minutes. This repeats L-0075. The owner made it a standing rule in
DEC-1073 (4). An earlier text-match kill also hit another agent's engineer.

proc.sh has no exec bit: run it as `bash .../tools/proc.sh wait --max <s> <pid>` (direct call: Permission denied, W2-189 lead 11-16).

**How to apply:** in a background chain, prefer `a && b` in one script. Otherwise use `proc.sh wait --max` on the
recorded pid. Related: [[standby-file-when-waiting]].
