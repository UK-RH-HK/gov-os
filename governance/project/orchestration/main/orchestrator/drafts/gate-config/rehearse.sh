#!/usr/bin/env bash
# DEC-1103 (1), ACT-GATE-CONFIG-1: the rehearsal, with HOME substituted by a throwaway home, so the real ~/.gov-os is
# never touched. Changes nothing live.
#   bash rehearse.sh            the log goes to rehearsal.log beside this file
# Layout: ~/gov-os-runs/GATE-CONFIG-rehearsal (made by this script, marked by its .gate-config-rehearsal file):
#   home/      the throwaway HOME; its .gov-os/machine starts as a copy of the real one (today: cpu-stat.json only)
#   backup/    apply.sh's records (GATE_BACKUP)
# W2-20's code runs from its worktree with the pin's interpreter. No test suite, no GPU work, no install, no commit.
set -u
MAIN=/home/usain/Dynamic-Agentic-Engineering-OS
HERE=$MAIN/.gov-runtime/scratch/orchestrator/drafts/gate-config
W=/home/usain/gov-os-worktrees/W2-20
BASE=/home/usain/gov-os-runs/GATE-CONFIG-rehearsal
T=$BASE/home
REAL=/home/usain/.gov-os/machine
LOG=${REHEARSAL_LOG:-$HERE/rehearsal.log}
exec > >(tee -a "$LOG") 2>&1
FAILS=0
read -r PY < /home/usain/.local/bin/gov; PY=${PY#'#!'}
say() { printf '\n== %s (%s)\n' "$1" "$(date '+%H:%M:%S')"; }
bad() { echo "REHEARSAL FAIL: $*"; FAILS=$((FAILS + 1)); }
act() { HOME=$T GATE_BACKUP=$BASE/backup bash "$HERE/apply.sh" "$@"; }
w2() { (cd "$W" && env -u GOV_TICKET HOME=$T PYTHONPATH="$W/src" PYTHONDONTWRITEBYTECODE=1 "$PY" "$@"); }
real_state() { ls -la "$REAL"; [ -e "$REAL/gate.json" ] && echo "REAL gate.json PRESENT" || echo "real gate.json: absent"; }
launch_gate() {  # $1 label, $2 GPU need (MiB or ""): the launcher's own admission step (_admit_start), as gov launch runs it
  w2 - "$2" <<'EOF'
import sys
from pathlib import Path
from gov.cli.errors import GovError
from gov.launch.launcher import _admit_start
need = int(sys.argv[1]) if sys.argv[1] else None
try:
    _admit_start(Path.cwd(), "engineer", "W2-20", None, need)
    print(f"gov launch's gate (engineer, GPU need {need}): ADMITTED")
    sys.exit(0)
except GovError as e:
    print(f"gov launch's gate (engineer, GPU need {need}): REFUSED {e.code}, exit {e.exit_code}: {e.message[:900]}")
    sys.exit(e.exit_code)
EOF
}

echo "rehearse.sh: $(date '+%F %T')"
say "live_before: the real machine folder"
real_state | tee "$BASE.real-before.txt"

say "prepare: the throwaway HOME"
if [ -e "$BASE" ]; then
  [ -f "$BASE/.gate-config-rehearsal" ] || { bad "$BASE exists and is not this script's"; exit 1; }
  rm -rf "$BASE"
fi
mkdir -p "$T/.gov-os" && : > "$BASE/.gate-config-rehearsal"
cp -a "$REAL" "$T/.gov-os/machine"
echo "HOME=$T; its machine folder: $(ls -A "$T/.gov-os/machine" | paste -sd' ')"

say "before: W2-20's gate with no file (what every launch meets after the merge, without this ACT)"
launch_gate before "" ; rc=$?
[ "$rc" = 3 ] && echo "-> refused, exit 3, on the missing file" || bad "the gate did not refuse without the file (exit $rc)"

say "check"
act check || bad "apply.sh check"

say "apply"
act apply || bad "apply.sh apply"
echo "--- the file written ($T/.gov-os/machine/gate.json):"
cat "$T/.gov-os/machine/gate.json"
w2 - <<'EOF' || bad "the file does not load clean"
from gov.resources import config
c = config.load()
print("config.load(): faults", c["faults"] or "none", "; due for re-measure:", c["due"] or "none")
raise SystemExit(1 if c["faults"] else 0)
EOF

say "idempotent: apply again, and init-config again"
s1=$(sha256sum "$T/.gov-os/machine/gate.json")
act apply || bad "a second apply did not end as 'already applied'"
(cd "$W" && HOME=$T PYTHONPATH="$W/src" PYTHONDONTWRITEBYTECODE=1 "$PY" -m gov.cli.main resources --init-config >/dev/null 2>"$BASE/init2.err"); rc=$?
echo "gov resources --init-config again: exit $rc: $(cat "$BASE/init2.err")"
[ "$rc" != 0 ] && grep -q RESOURCE_CONFIG_EXISTS "$BASE/init2.err" || bad "a second init did not refuse"
[ "$s1" = "$(sha256sum "$T/.gov-os/machine/gate.json")" ] && echo "the file is unchanged by both" || bad "the file changed"

say "admits: W2-20's gate on the file"
launch_gate session "" || bad "a session launch is refused"
launch_gate small-gpu 1024; rc=$?
[ "$rc" = 3 ] && echo "-> FINDING (W2-20's, not the file's): a launch declaring 1024 MiB (kind other) is refused while the GPU has 9+ GB free: WSL's nvidia-smi gives no per-process memory ([N/A]), so no share reads as held and the embedder's and reranker's whole shares (7 GiB) plus the headroom are kept back on top of what the loaded embedders already use"
(cd "$W" && HOME=$T PYTHONPATH="$W/src" PYTHONDONTWRITEBYTECODE=1 "$PY" -m gov.cli.main resources --check --gpu-need-mib 1024 --gpu-kind embedder > "$BASE/check-gpu-embedder.json" 2>&1)
rc=$?; echo "gov resources --check --gpu-need-mib 1024 --gpu-kind embedder (the first share): exit $rc"
[ "$rc" = 0 ] || { bad "an embedder's 1024 MiB start is refused"; head -c 600 "$BASE/check-gpu-embedder.json"; }
for k in session test rebuild; do
  (cd "$W" && HOME=$T PYTHONPATH="$W/src" PYTHONDONTWRITEBYTECODE=1 "$PY" -m gov.cli.main resources --check --kind $k > "$BASE/check-$k.json" 2>&1)
  rc=$?; echo "gov resources --check --kind $k: exit $rc"; [ "$rc" = 0 ] || { bad "--kind $k refused"; head -c 800 "$BASE/check-$k.json"; }
done
python3 - "$BASE/check-session.json" <<'EOF'
import json, sys
r = json.load(open(sys.argv[1]))
t, m = r["thresholds"], r["memory"]
print(f"reading: nproc {r['nproc']}; load {r['load_1m']}/{r['load_15m']}; busy cores {r['busy_cores']}; memory have "
      f"{m['have_bytes']/2**30:.1f} GiB, need {m['need_bytes']/2**30:.1f} GiB (floor + newcomer); disk free "
      f"{r['disk']['free_bytes']/2**30:.0f} GiB (floor {t['disk_floor_bytes']/2**30:.0f}), inodes {r['disk']['free_inodes']:,} "
      f"(floor {t['inode_floor']:,}); slots {r['slots']['count']} ({r['slots']['held']} held); servers "
      + ", ".join(f"{k} pid {v['pid']}" for k, v in r["servers"].items())
      + f"; due for re-measure: {r['config']['due_for_remeasure']}; gate open: {r['gate']['open']}")
EOF

say "refuses over the limits"
launch_gate over-gpu 20000; rc=$?
[ "$rc" = 3 ] && echo "-> refused, exit 3 (20000 MiB is above the card's 16303 MiB)" || bad "the over-limit GPU launch was not refused (exit $rc)"
(cd "$W" && HOME=$T GOV_RESOURCES_NPROC=1 PYTHONPATH="$W/src" PYTHONDONTWRITEBYTECODE=1 "$PY" -m gov.cli.main resources --check > "$BASE/check-nproc1.json" 2>&1); rc=$?
echo "gov resources --check, the machine read as 1 processor (GOV_RESOURCES_NPROC=1, the load and CPU limits): exit $rc: $(head -c 400 "$BASE/check-nproc1.json")"
[ "$rc" = 3 ] || bad "the load limit did not refuse"

say "undo"
act undo || bad "apply.sh undo"
[ -e "$T/.gov-os/machine/gate.json" ] && bad "the file is still there" || echo "the file is gone"
launch_gate after-undo ""; rc=$?
[ "$rc" = 3 ] && echo "-> refused again without the file (undo restores the state before)" || bad "after undo the gate admits (exit $rc)"
diff <(ls -A "$REAL") <(ls -A "$T/.gov-os/machine") >/dev/null && echo "the throwaway machine folder holds the same names as before the apply" \
  || { echo "the throwaway machine folder: $(ls -A "$T/.gov-os/machine" | paste -sd' ')"; }

say "live_after: the real machine folder"
real_state > "$BASE.real-after.txt"; cat "$BASE.real-after.txt"
grep -q "REAL gate.json PRESENT" "$BASE.real-after.txt" && bad "a real gate.json appeared"
diff <(awk '{print $NF}' "$BASE.real-before.txt") <(awk '{print $NF}' "$BASE.real-after.txt") >/dev/null \
  && echo "the real machine folder: the same names before and after (no file added or removed)" || bad "the real machine folder changed"

echo; echo "rehearse.sh: done $(date '+%F %T'): $FAILS failure(s)"
exit $((FAILS > 0))
