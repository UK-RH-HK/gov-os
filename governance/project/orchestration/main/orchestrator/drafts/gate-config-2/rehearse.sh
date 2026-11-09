#!/usr/bin/env bash
# ACT-GATE-CONFIG-2: the rehearsal, with HOME substituted by a throwaway home whose machine folder starts as a copy of
# the real one (ACT-GATE-CONFIG-1's gate.json included), so the real ~/.gov-os is never touched. Changes nothing live.
#   bash rehearse.sh            the log goes to rehearsal.log beside this file
# Layout: ~/gov-os-runs/GATE-CONFIG-2-rehearsal (made by this script, marked by its .gate-config-2-rehearsal file):
#   home/      the throwaway HOME
#   backup/    apply.sh's records (GATE_BACKUP)
# W2-20's code runs from its worktree with the pin's interpreter. No test suite, no GPU work, no install, no commit.
set -u
MAIN=/home/usain/Dynamic-Agentic-Engineering-OS
HERE=$MAIN/.gov-runtime/scratch/orchestrator/drafts/gate-config-2
W=/home/usain/gov-os-worktrees/W2-20
BASE=/home/usain/gov-os-runs/GATE-CONFIG-2-rehearsal
T=$BASE/home
REAL=/home/usain/.gov-os/machine
OLD_SHA=de4fb326288d80d9d627ad910542ae5d86834c98a3d8895c0e16b9ece2fcd457
NEW_SHA=52e32fc182d6e07c856512eb6926e7442eb16c856b46194f35d522e238c44034
LOG=${REHEARSAL_LOG:-$HERE/rehearsal.log}
: > "$LOG"
exec > >(tee -a "$LOG") 2>&1
FAILS=0
read -r PY < /home/usain/.local/bin/gov; PY=${PY#'#!'}
say() { printf '\n== %s (%s)\n' "$1" "$(date '+%H:%M:%S')"; }
bad() { echo "REHEARSAL FAIL: $*"; FAILS=$((FAILS + 1)); }
act() { HOME=$T GATE_BACKUP=$BASE/backup bash "$HERE/apply.sh" "$@"; }
w2() { (cd "$W" && env -u GOV_TICKET HOME=$T PYTHONPATH="$W/src" PYTHONDONTWRITEBYTECODE=1 "$PY" "$@"); }
real_state() { ls -la "$REAL"; [ -e "$REAL/gate.json" ] && echo "real gate.json sha256 $(sha256sum "$REAL/gate.json" | cut -d' ' -f1)"; }
launch_gate() {  # $1 label, $2 GPU need (MiB or ""): the launcher's own admission step (_admit_start), as gov launch runs it
  w2 "$HERE/launch_gate.py" "$2"
}

echo "rehearse.sh: $(date '+%F %T'); W2-20 at $(git -C "$W" rev-parse --short=12 HEAD)"
say "live_before: the real machine folder"
real_state | tee "$BASE.real-before.txt"

say "prepare: the throwaway HOME"
if [ -e "$BASE" ]; then
  [ -f "$BASE/.gate-config-2-rehearsal" ] || { bad "$BASE exists and is not this script's"; exit 1; }
  rm -rf "$BASE"
fi
mkdir -p "$T/.gov-os" && : > "$BASE/.gate-config-2-rehearsal"
cp -a "$REAL" "$T/.gov-os/machine"
echo "HOME=$T; its machine folder: $(ls -A "$T/.gov-os/machine" | paste -sd' '); gate.json $(sha256sum "$T/.gov-os/machine/gate.json" | cut -d' ' -f1)"

say "before: W2-20's gate (28fbcfebf) on ACT-1's file (round 1's key names)"
launch_gate before "" ; rc=$?
[ "$rc" != 0 ] && echo "-> refused (LAUNCH_REFUSED, exit $rc) on the old file's key names: what blocks round 3's launch today" || bad "the gate did not refuse on the old file (exit $rc)"

say "check"
act check || bad "apply.sh check"

say "apply"
act apply || bad "apply.sh apply"
echo "--- the file written ($T/.gov-os/machine/gate.json):"
cat "$T/.gov-os/machine/gate.json"
[ "$(sha256sum "$T/.gov-os/machine/gate.json" | cut -d' ' -f1)" = "$NEW_SHA" ] && echo "-> the written bytes are the rehearsed ones ($NEW_SHA)" || bad "the written bytes differ"
[ "$(sha256sum "$BASE/backup/gate.json.act1" | cut -d' ' -f1)" = "$OLD_SHA" ] && echo "-> ACT-1's file kept at backup/gate.json.act1 ($OLD_SHA)" || bad "ACT-1's file not kept"
w2 - <<'EOF' || bad "the file does not load clean"
from gov.resources import config
c = config.load()
print("config.load():", {k: v for k, v in c.items() if k in ("faults", "due", "due_for_remeasure")})
raise SystemExit(1 if c.get("faults") else 0)
EOF

say "idempotent: apply again, and init-config again"
s1=$(sha256sum "$T/.gov-os/machine/gate.json")
act apply || bad "a second apply did not end as 'already applied'"
(cd "$W" && HOME=$T PYTHONPATH="$W/src" PYTHONDONTWRITEBYTECODE=1 "$PY" -m gov.cli.main resources --init-config >/dev/null 2>"$BASE/init2.err"); rc=$?
echo "gov resources --init-config again: exit $rc: $(head -c 300 "$BASE/init2.err")"
[ "$rc" != 0 ] && grep -q RESOURCE_CONFIG_EXISTS "$BASE/init2.err" || bad "a second init did not refuse"
[ "$s1" = "$(sha256sum "$T/.gov-os/machine/gate.json")" ] && echo "the file is unchanged by both" || bad "the file changed"

say "admits: W2-20's gate on the new file"
launch_gate session "" || bad "a session launch is refused"
launch_gate small-gpu 1024; rc=$?
[ "$rc" = 0 ] && echo "-> a launch declaring 1024 MiB (kind other) is admitted with the GPU's free memory (round 2's [N/A] handling)" \
  || echo "-> NOTE: a launch declaring 1024 MiB (kind other) is refused (exit $rc)"
(cd "$W" && HOME=$T PYTHONPATH="$W/src" PYTHONDONTWRITEBYTECODE=1 "$PY" -m gov.cli.main resources --check > "$BASE/check-session.json" 2>&1)
rc=$?; echo "gov resources --check (the start check): exit $rc"; [ "$rc" = 0 ] || { bad "the start check refused"; head -c 800 "$BASE/check-session.json"; }
echo "--- the session reading (first 1500 characters):"; head -c 1500 "$BASE/check-session.json"; echo

say "refuses over the limits"
launch_gate over-gpu 20000; rc=$?
[ "$rc" != 0 ] && echo "-> refused (LAUNCH_REFUSED, exit $rc): 20000 MiB is above the card's 16303 MiB" || bad "the over-limit GPU launch was not refused (exit $rc)"
echo "5.00 5.00 5.00 1/1 1" > "$BASE/loadavg-high"
(cd "$W" && HOME=$T GOV_RESOURCES_NPROC=4 GOV_RESOURCES_LOADAVG="$BASE/loadavg-high" PYTHONPATH="$W/src" PYTHONDONTWRITEBYTECODE=1 "$PY" -m gov.cli.main resources --check > "$BASE/check-load.json" 2>&1); rc=$?
echo "gov resources --check, a planted load of 5.0 on 4 processors (GOV_RESOURCES_LOADAVG, GOV_RESOURCES_NPROC): exit $rc"
[ "$rc" = 3 ] || bad "the load limit did not refuse"

say "undo"
act undo || bad "apply.sh undo"
[ "$(sha256sum "$T/.gov-os/machine/gate.json" | cut -d' ' -f1)" = "$OLD_SHA" ] && echo "-> ACT-1's file is back ($OLD_SHA)" || bad "ACT-1's file is not back"
launch_gate after-undo ""; rc=$?
[ "$rc" != 0 ] && echo "-> refused again on the old file (undo restores the state before)" || bad "after undo the gate admits (exit $rc)"
diff <(ls -A "$REAL") <(ls -A "$T/.gov-os/machine") >/dev/null && echo "the throwaway machine folder holds the same names as the real one" \
  || echo "the throwaway machine folder: $(ls -A "$T/.gov-os/machine" | paste -sd' ')"

say "live_after: the real machine folder"
real_state > "$BASE.real-after.txt"; cat "$BASE.real-after.txt"
grep -q "$OLD_SHA" "$BASE.real-after.txt" || bad "the real gate.json changed"
diff <(awk '{print $NF}' "$BASE.real-before.txt" | grep -v '^[0-9a-f]\{64\}$') <(awk '{print $NF}' "$BASE.real-after.txt" | grep -v '^[0-9a-f]\{64\}$') >/dev/null \
  && echo "the real machine folder: the same names before and after, gate.json unchanged" || bad "the real machine folder changed"

echo; echo "rehearse.sh: done $(date '+%F %T'): $FAILS failure(s)"
exit $((FAILS > 0))
