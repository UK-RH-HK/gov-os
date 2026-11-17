---
name: standby-file-when-waiting
description: "Write the CTO stand-by file whenever waiting on the owner or the operator, so the sentinel does not false-alarm"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 33b3628c-7145-4e49-bfd8-2cfd894e92c4
  modified: 2026-11-10T21:02:10.436Z
---

Whenever the CTO waits on the owner or the owner's operator (an ACT, a decision), write
`.gov-runtime/scratch/orchestrator/log/cto-standby.txt` with the time and what is awaited, and end it (`mv` to
`cto-standby.ended-<HHMM>.txt`, never `rm`) when the wait ends.

**Why:** the sentinel's dead-man check (`tools/deadman.py`, DEC-998) alerts when the CTO's session writes nothing for
an hour, unless that file exists. On 2026-11-04 it raised a false ALERT at 11:43 while the CTO waited idle on the
owner's re-pin ACT, then fell silent until the operator restarted its watch.

**How to apply:** the moment a hand-over or question to the owner leaves the CTO idle, write the file in the same
turn. Start the note with its UTC time (`YYYY-MM-DD HH:MM:SS`), and rewrite the whole file to renew it, never append:
under DEC-1123 (5) / ACT-DEADMAN-STANDBY-1 the dead-man ages a note by that leading time (else its mtime) and stops
honouring it after the limit (2 h proposed). End the note before any hand-over: on 2026-11-10 a handed-over note
muted the dead-man from 15:49 to 19:18. Related: [[act-hold-file]] (the separate `act-in-progress.txt` hold during
an owner ACT).
