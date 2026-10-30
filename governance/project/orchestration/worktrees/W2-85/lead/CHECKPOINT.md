# Lead checkpoint — DAEO-gdzh (W2-85), run 1

- Branch `w2/W2-85`, start head `403d70b396ff` (clean). LITE, test-revision ticket; no engineer, no review.
- Loop count: 0 (no implementer).
- 18:35 started. Identity checks OK. Read: ticket, serial-only.txt, serial.py, plugin, W1-30 r11 KINDS, W2-57 list cases, W2-54 README, DEC-951/953/954.
- 18:4x rebuild started in the background (flock), log `.gov-runtime/scratch/lead/log/rebuild.{json,err,rc}`.
- Next: launch test designer (brief `briefs/td-1.md`, tripwire `tripwire-before-1.json`), then the checks of step 2.

## Discoveries so far
- `close_build.py` (the orchestrator's close tool under DEC-953) takes every entry of the list into its serial phase (`entries(clone)`), nightly ones included; it does not use `gov.close.serial.phase`. So under close_build the routed cases run alone in the serial phase, not left out. Outside this ticket's paths: name it in the return.
- `test_w2_54_sandboxed_worker.py` already carries a `nightly: live-session` line (W2-60a's?).
- Inside a close, the green-here fixture reads the close's check result (W2-75) and asks no embedder; as the nightly runs it (no GOV_CLOSE_CHECK_RESULT) it runs gov check itself.

## Brief gaps (running)
- none yet

## Guard read refusals: 0
