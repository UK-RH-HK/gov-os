#!/usr/bin/env bash
# E5's live part on the fresh 80 (data only, not judged; DEC-1097 (1)(c); from drafts/d4b/e5_live.sh): a SECOND live
# retrieval of the 80 through the pinned gov on E0's clone with a page of 40 (--batch-size 20) within 12,000 tokens,
# every search's output kept, so fresh80_data.py e5 takes each question's first bundle. After the judged reader run
# and after the hold ends. One GPU job, its own process group, the backstop armed. No store rebuild; the store's
# sha256 recorded before and after (a change is reported). Run once (refused when its folder exists).
#   setsid bash f80_e5_live.sh --sets-root ~/gov-os-eval > ~/gov-os-runs/fresh-80/e5-live.out 2>&1 < /dev/null &
# The folder <root>/runs/fresh-80/data/e5/live (kept/, measure.txt) is derived here. Counts only on standard output.
set -uo pipefail
REPO=/home/usain/Dynamic-Agentic-Engineering-OS; O=$REPO/.gov-runtime/scratch/orchestrator; F=$O/drafts/fresh80
PINPY=$HOME/.local/share/gov-os/pin-bcea09060ebc/bin/python; GOV=$HOME/.local/bin/gov
CLONE=$HOME/gov-os-runs/D4B/w4-e0/repo; HEAVY=$O/tools/heavy_slot.sh; BACKSTOP=$O/tools/gpu_backstop.sh
PROC=$O/tools/proc.sh; HOLD=$O/log/act-in-progress.txt; TMPD=/tmp/gov-os-emg-f80e5; PINFILE=$F/FRESH80-REVIEWED.sha256
SETS_ROOT=""
while [ $# -gt 0 ]; do case "$1" in --sets-root) SETS_ROOT=${2:-}; shift 2 || exit 2;; --sets-root=*) SETS_ROOT=${1#*=}; shift;; *) echo "REFUSED: --sets-root <root> only"; exit 2;; esac; done
pinned() { [ -s "$PINFILE" ] && ( cd "$F" && sha256sum --quiet -c "$PINFILE" ) > /dev/null 2>&1; }
own_group() { [ "$(ps -o pgid= -p $$ | tr -d ' ')" = "$$" ]; }
ERRF=/dev/null
ROOT=$(realpath -e "$SETS_ROOT" 2>/dev/null) || { echo "REFUSED: --sets-root <root> is required"; exit 2; }
RUNS=$ROOT/runs/fresh-80; D=$RUNS/data/e5/live
say() { case "$*" in *memory-verdict-2/*|*fresh-80/*|*"$ROOT/"*) echo "REFUSED: a line naming a hidden folder was not printed"; exit 3 ;; esac; echo "$*"; }
refuse() { say "REFUSED: $*"; exit 2; }
check() { "$PINPY" "$F/f80_check.py" "$@" 2>> "$ERRF"; }
# --- the stubs line (tests only)
[ -z "${GOV_STORE+x}" ] || refuse "GOV_STORE is set (reviewer 1 S6): unset it"
own_group || refuse "not in its own process group: start it with setsid"
check act --sets-root "$ROOT" || refuse "ACT-GUARD-SETS-1 is not applied (readiness-7 F1)"
[ -e "$RUNS/COUNTS" ] && [ -s "$RUNS/reader/summary.json" ] && python3 -c "import json,sys; d=json.load(open(sys.argv[1])); sys.exit(0 if d.get('rows') == d.get('questions_planned') and not d.get('stopped') else 1)" "$RUNS/reader/summary.json" 2>/dev/null \
  || refuse "the judged run is not finished (every question run, no brake stop): E5 runs after it (review R4)"
grep -q "FRESH-80 HOLD" "$HOLD" 2>/dev/null && refuse "the hold is on: data conditions run after it ends"
[ ! -e "$D" ] || refuse "E5's live part has run already: never twice"
pinned || refuse "the fresh-80 files are not as pinned"
check clone --clone "$CLONE" > /dev/null || refuse "the clone is not as E0 left it"
unset GOV_STORE GOV_TICKET
mkdir -p "$D/kept" "$TMPD" 2>/dev/null; ERRF=$RUNS/data/e5/live.err; exec 2>> "$ERRF"; : > "$D/kept/.n"; : > "$D/ms"
ST0=$(check store --clone "$CLONE")
G=$(ps -o pgid= -p $$ | tr -d ' '); setsid bash "$BACKSTOP" "$G" < /dev/null > /dev/null 2>&1 & BS=$!
trap 'bash "$PROC" stop --grace 5 "$BS" > /dev/null 2>&1' EXIT
say "== $(date '+%F %T') E5 live on the 80 (data only): page 40, budget 12000; backstop $BS; store ${ST0:0:16}"
t0=$(date +%s)
env -u GOV_STORE -u GOV_TICKET GOV_ROLE=orchestrator GOV_KEEP="$D/kept" GOV_MS="$D/ms" TMPDIR="$TMPD" \
  bash "$HEAVY" "$PINPY" -m gov.retrieval.measure memory-verdict-2 --root "$CLONE" --sets-root "$ROOT" --part hidden \
  --batch-size 20 --bundle-budget 12000 --out "$D" --gov "$RUNS/gov" > "$D/measure.txt" 2> "$D/measure.err"; rc=$?
ST1=$(check store --clone "$CLONE")
say "E5 live: exit $rc; $(( $(date +%s) - t0 )) s; question lines $(grep -c ' (hidden): hit@5 ' "$D/measure.txt"); kept $(ls "$D/kept" | grep -c '^[0-9]*\.json$'); store $([ "$ST0" = "$ST1" ] && echo unchanged || echo 'CHANGED: reported')"
exit $rc
