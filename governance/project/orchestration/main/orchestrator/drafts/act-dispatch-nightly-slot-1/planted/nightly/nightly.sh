#!/bin/bash
# A planted nightly for ACT-DISPATCH-NIGHTLY-SLOT-1's rehearsal: nightly.sh's slot form (DEC-984) and nothing else.
# Usage: bash <bed>/nightly/nightly.sh night   with PN_ORCH (the planted orchestrator folder), PN_RUNS (the planted run
# folder), PN_SLOT_DIR (the planted slot folder: never /tmp's real slots), PN_HOLD (1: flock the fds, 0: open only),
# PN_RUN_CWD (where the suite stand-in runs; default the clone), PN_SECONDS (how long it runs).
set -u
: "${PN_ORCH:?}" "${PN_RUNS:?}" "${PN_SLOT_DIR:?}"
case "$PN_SLOT_DIR" in /tmp/gov-os-heavy-slot*|/tmp|/tmp/) echo "refused: the real slot folder" >&2; exit 9 ;; esac
CLONE=$PN_RUNS/20261113-0404
mkdir -p "$CLONE" "$PN_ORCH"
date '+%F %T nightly: running (a marker only, DEC-961)' > "$PN_ORCH/NIGHTLY-RUNNING"
cd "$CLONE" || exit 2
SLOT_FDS=()
for i in 1 2 3; do
  unset sfd
  { exec {sfd}>"$PN_SLOT_DIR/gov-os-heavy-slot-$i.lock"; } 2>/dev/null || continue
  SLOT_FDS+=("$sfd")
  [ "${PN_HOLD:-1}" = 1 ] && flock -w 5 "$sfd"
done
noslot() {
  local f
  for f in "${SLOT_FDS[@]}"; do [ -n "$f" ] && eval "exec $f>&-"; done
  cd "${PN_RUN_CWD:-$CLONE}" || exit 2
  exec "$@"
}
# the suite's stand-in: argv read as a heavy pytest (python3 ... -m pytest tests), a sleep in fact; no test runs
( noslot python3 -c "import time; time.sleep(${PN_SECONDS:-30})" -m pytest tests )
for f in "${SLOT_FDS[@]}"; do [ -n "$f" ] && eval "exec $f>&-"; done
rm -f "$PN_ORCH/NIGHTLY-RUNNING"
