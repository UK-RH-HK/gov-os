# Lead checkpoint — DAEO-cy5o (W2-57), run 1

- **State:** start of run 1. Head `d54546f00b21` (claim commit), tree clean. Identity checked (orchestrator, DAEO-cy5o).
- **Decided (lead):** test design in two batches in one session (td-1 = KPI 1 probe + KPI 2 doctor; resume = batch B, KPIs 3-7). Then engineer batches (probe+doctor; then serial list etc.).
- **Found, to package at return (blocks part only):** the ticket's allowed_paths have `src/gov/close/serial.py` (new) but not `src/gov/close/command.py` (nor the serial-only plugin). The live/real-model route to the nightly needs the close's serial phase to leave nightly-kind entries out; that call is in command.py. Package P-W2-57-PATHS (widen to command.py, the serial phase's call only). Also W1-19's files are not in the designer's named files (W2-M332's sampler change, KPI 5) — the designer is told to package it if needed.
- **Next:** launch td-1 (gov launch, sandboxed, xhigh), tripwire n=1.
- **Loop count:** 0 implementer iterations.
