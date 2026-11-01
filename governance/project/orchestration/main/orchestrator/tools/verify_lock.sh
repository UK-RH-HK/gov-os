#!/usr/bin/env bash
# A lead's test run (owner, DEC-961, DEC-962, DEC-968, DEC-979 D1). Since DEC-968 no lead runs the full suite, so a
# lead's run is always the scoped set. Since DEC-979 D1 (2026-10-31 23:50) it takes one of the machine's heavy-job
# slots (heavy_slot.sh, sizes in heavy_slots.conf) and waits for one; the name is kept because every lead brief calls it.
#   bash verify_lock.sh <the run's command and arguments>
# Exits with the command's code.
exec bash "$(cd "$(dirname "$0")" && pwd)/heavy_slot.sh" "$@"
