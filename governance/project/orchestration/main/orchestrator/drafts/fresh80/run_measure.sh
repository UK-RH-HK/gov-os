#!/usr/bin/env bash
# The fresh 80's one measure (FRESH-80-1 §2 items 5, 11 to 15, §3.2 steps 7 and 8, §3.5; DEC-1097 (1)(b), (g), (2)).
#   setsid bash run_measure.sh --sets-root ~/gov-os-eval [--restart] > ~/gov-os-runs/fresh-80/measure.out 2>&1 < /dev/null &
# Its own process group (it refuses otherwise; record $! and wait or stop by that pid or -pgid only, tools/proc.sh).
# The run folder <root>/runs/fresh-80 and the set are derived here from the sets root; standard output carries ids and
# counts only (say refuses a line naming a hidden folder); every helper's standard error goes to the run folder.
#  1. refusals, nothing written: GOV_STORE set (reviewer 1 S6); ACT-GUARD-SETS-1 not applied (by content: the main
#     tree's sets_root_hidden block with runs/fresh-80/** and the live hook's sets-root rule; readiness-7 F1); USED
#     there (one shot, item 14) unless --restart; the hold not begun ("FRESH-80 HOLD" in log/act-in-progress.txt, item
#     13); the reviewed files not as pinned; the pre-flight not clean; the declaration not committed, a blank left, or
#     its digest not the set's now and the pre-flight's (readiness-7 F6, F12); the clone not clean at c00d525f with
#     window 4's pool, or gov not at the pin (item 12); less than 2 GiB free for the run folder or /tmp (review R5).
#  2. recorded before: integrate's head, the integration store log's length, the clone's store.db sha256; the run
#     lock taken (one runner at a time, review R3).
#  3. the GPU backstop armed on this group. NO store rebuild (reviewer 1 S7): the 80 runs on E0's clone and its store
#     as they are (written 2026-11-07 15:58).
#  4. before each attempt (the first, and before the one restart; review R1): the live reranker READY from the pin
#     and a probe search answered by the shared service with every route; the control on the visible 40 (the same
#     command; the families line of item 5, hit@5 34 +- 2, every kept search answered by the shared service with
#     every route); the families line again; the declaration's digest again. Any of these failing: STOP before the
#     attempt's folder exists. On a first start the set stays unused; before the restart, nothing is spent: the
#     restart does not run into the same outage, and --restart stays open for when the servers are back (owner).
#  5. USED written (noclobber) before the first search of the 80.
#  6. the 80: memory-verdict-2 --part hidden as e0_run.sh ran the 138: the pin's python, default budgets (batch 10,
#     bundle 6,000, stack 24,000), GOV_ROLE=orchestrator, GOV_STORE and GOV_TICKET unset, the GOV_KEEP wrapper, E0's
#     clone, through heavy_slot.sh; into a new folder attempt-1 (kept/, measure.txt, measure.err, ms).
#  7. §3.5's fault rule: a non-zero exit, an output not whole, or a search answered otherwise than declared (rerank.by
#     not the shared service, a route missing or unavailable, the pool's rerank fallen back: code review F1) is a
#     fault: the attempt is kept and named, and ONE restart follows, after step 4's checks, into attempt-2, whatever
#     the partial figures show; a fault in attempt-2 stops everything (STOPPED), to the owner. A backstop trip or a
#     machine stop freezes or ends this script: stop its group by its pgid and start it again with --restart (allowed
#     once). The store's sha256 changed over an attempt stops everything (a restart could not run on the same store).
#  8. recorded after: integrate's head (a moved head is reported), the integration store log's new lines (reviewer 1
#     S5), the store's sha256; COUNTS names the attempt whose figures count.
# Exit 0: an attempt counts; 1: stopped; 2: refused before anything was written. No hit@5 of the 80 is printed here.
set -uo pipefail
REPO=/home/usain/Dynamic-Agentic-Engineering-OS; O=$REPO/.gov-runtime/scratch/orchestrator; F=$O/drafts/fresh80
PINPY=$HOME/.local/share/gov-os/pin-bcea09060ebc/bin/python; GOV=$HOME/.local/bin/gov
CLONE=$HOME/gov-os-runs/D4B/w4-e0/repo; LIVE_LOG=$HOME/.cache/gov-os/rerank.log
HEAVY=$O/tools/heavy_slot.sh; BACKSTOP=$O/tools/gpu_backstop.sh; PROC=$O/tools/proc.sh
ISLOG=$O/log/integration-store.log; HOLD=$O/log/act-in-progress.txt; TMPD=/tmp/gov-os-emg-f80
PINFILE=$F/FRESH80-REVIEWED.sha256; FREE_KIB=2097152
SETS_ROOT=""; RESTART=0
while [ $# -gt 0 ]; do
  case "$1" in
    --sets-root) SETS_ROOT=${2:-}; shift 2 || { echo "REFUSED: --sets-root needs a value"; exit 2; } ;;
    --sets-root=*) SETS_ROOT=${1#*=}; shift ;;
    --restart) RESTART=1; shift ;;
    *) echo "REFUSED: unknown argument (the form: --sets-root <root> [--restart])"; exit 2 ;;
  esac
done
pinned() { [ -s "$PINFILE" ] && ( cd "$F" && sha256sum --quiet -c "$PINFILE" ) > /dev/null 2>&1; }
own_group() { [ "$(ps -o pgid= -p $$ | tr -d ' ')" = "$$" ]; }
free_ok() { local d; for d in "$1" /tmp; do [ "$(df -Pk "$d" 2>/dev/null | awk 'NR==2 {print $4}')" -ge "$FREE_KIB" ] 2>/dev/null || return 1; done; }
ERRF=/dev/null  # every helper's standard error: never the log (a traceback could name a path)
[ -n "$SETS_ROOT" ] || { echo "REFUSED: --sets-root is required"; exit 2; }
ROOT=$(realpath -e "$SETS_ROOT" 2>/dev/null) || { echo "REFUSED: the sets root does not exist"; exit 2; }
RUNS=$ROOT/runs/fresh-80; USED=$RUNS/USED; COUNTS=$RUNS/COUNTS
say() {  # ids and counts only: a line naming a hidden folder is not printed
  case "$*" in *memory-verdict-2/*|*fresh-80/*|*"$ROOT/"*) echo "REFUSED: a line naming a hidden folder was not printed"; exit 3 ;; esac
  echo "$*"
}
refuse() { say "REFUSED: $*"; exit 2; }
check() { "$PINPY" "$F/f80_check.py" "$@" 2>> "$ERRF"; }
# --- the stubs line (tests only: test_run_measure.py runs a copy with one line here; the copy less it is this file)

# ---- 1. refusals: nothing is written before every one passes
[ -z "${GOV_STORE+x}" ] || refuse "GOV_STORE is set: the measure would search the store it names, not the clone's (W2-116; reviewer 1 S6). Unset it and start again"
own_group || refuse "not in its own process group: start it with setsid (record \$! to wait or stop by pid)"
check act --sets-root "$ROOT" --repo "$REPO" || refuse "ACT-GUARD-SETS-1 is not applied: nothing is written (DEC-1097 (2); readiness-7 F1)"
ATTEMPTS=$(ls -d "$RUNS"/attempt-* 2>/dev/null | wc -l)
if [ "$RESTART" = 0 ]; then
  [ ! -e "$USED" ] || refuse "the fresh 80 is used (USED exists): the measure never runs twice (FRESH-80-1 item 14)"
else
  [ -e "$USED" ] || refuse "--restart, but the set is not used: start without --restart"
  [ ! -e "$COUNTS" ] && [ ! -e "$RUNS/STOPPED" ] && [ ! -e "$RUNS/attempt-2" ] \
    && { [ "$ATTEMPTS" = 0 ] || { [ -d "$RUNS/attempt-1" ] && [ ! -e "$RUNS/attempt-1/DONE" ]; }; } \
    || refuse "--restart is allowed once: attempt-1 started and not done (or none started), no attempt-2, nothing counted or stopped"
fi
grep -q "FRESH-80 HOLD" "$HOLD" 2>/dev/null || refuse "the hold has not begun (log/act-in-progress.txt with the line FRESH-80 HOLD; FRESH-80-1 item 13)"
pinned || refuse "the reviewed fresh-80 files are not as pinned (FRESH80-REVIEWED.sha256)"
check preflight --sets-root "$ROOT" || refuse "the pre-flight has not run clean"
check declared --sets-root "$ROOT" --repo "$REPO" || refuse "the declaration is not committed whole with the set's digest (readiness-7 F6, F12)"
check clone --clone "$CLONE" || refuse "the clone is not as E0 left it (item 12)"
free_ok "$ROOT" || refuse "less than 2 GiB free for the run folder or /tmp (review R5)"
unset GOV_STORE GOV_TICKET

# ---- 2. recorded before; the lock
mkdir -p "$RUNS" "$TMPD" 2>/dev/null; chmod 700 "$RUNS" 2>/dev/null; ERRF=$RUNS/run_measure.err; exec 2>> "$ERRF"
exec 8> "$RUNS/.run.lock"
flock -n 8 || { say "STOP: another run_measure.sh holds the run lock"; exit 1; }
INT0=$(git -C "$REPO" rev-parse refs/heads/w2/integrate 2>/dev/null || echo none)
IS0=$(wc -l < "$ISLOG" 2>/dev/null || echo 0)
ST0=$(check store --clone "$CLONE")
say "== $(date '+%F %T') the fresh 80's measure (restart: $RESTART); integrate at ${INT0:0:12}; store sha256 ${ST0:0:16}; pin $(readlink -f "$GOV" | sed 's#.*/\(pin-[^/]*\)/.*#\1#')"

# ---- 3. the backstop on this group; the wrapper (e0_run.sh's GOV_KEEP form)
BS=""; CUR=""
finish() {
  local rc=$?
  trap - EXIT
  [ -n "$CUR" ] && [ ! -e "$RUNS/$CUR/DONE" ] && [ ! -e "$RUNS/$CUR/FAULT" ] && echo "interrupted (exit $rc)" > "$RUNS/$CUR/FAULT"
  [ -n "$BS" ] && bash "$PROC" stop --grace 5 "$BS" > /dev/null 2>&1
  exit $rc
}
trap finish EXIT; trap 'exit 130' INT; trap 'exit 143' TERM
G=$(ps -o pgid= -p $$ | tr -d ' ')
setsid bash "$BACKSTOP" "$G" < /dev/null > /dev/null 2>&1 & BS=$!
sleep 1; kill -0 "$BS" 2>/dev/null || { say "STOP: the GPU backstop did not stay up"; exit 1; }
say "backstop pid $BS on group $G"
W=$RUNS/gov
cat > "$W" <<EOG
#!/usr/bin/env bash
if [ "\$1" = retrieve ] && [ -n "\${GOV_KEEP:-}" ]; then
  n=\$(flock "\$GOV_KEEP/.n.lock" sh -c 'n=\$(cat "\$0/.n" 2>/dev/null || echo 0); n=\$((n+1)); echo \$n > "\$0/.n"; echo \$n' "\$GOV_KEEP")
  s=\$(date +%s%N); "$GOV" "\$@" | tee "\$GOV_KEEP/\$(printf %05d \$n).json"; rc=\${PIPESTATUS[0]}
  echo \$(( (\$(date +%s%N) - s) / 1000000 )) >> "\$GOV_MS"; exit \$rc
fi
exec "$GOV" "\$@"
EOG
chmod 700 "$W"

measure() {  # measure <set> <part> <folder>: the measure as e0_run.sh ran it, into a new folder
  local S=$1 P=$2 D=$3
  mkdir "$D" 2>/dev/null || return 9
  mkdir -p "$D/kept"; : > "$D/kept/.n"; : > "$D/ms"
  env -u GOV_STORE -u GOV_TICKET GOV_ROLE=orchestrator GOV_KEEP="$D/kept" GOV_MS="$D/ms" TMPDIR="$TMPD" \
    bash "$HEAVY" "$PINPY" -m gov.retrieval.measure "$S" --root "$CLONE" --sets-root "$ROOT" --part "$P" \
    --out "$D" --gov "$W" > "$D/measure.txt" 2> "$D/measure.err"
}
median() { sort -n "$1" | awk '{a[NR]=$1} END {if (NR) print a[int((NR+1)/2)]; else print "-"}'; }

# ---- 4. before each attempt: the live service, the control, the families line, the declaration's digest
ready() {
  local k rc t0
  check live --clone "$CLONE" --gov "$GOV" --log "$LIVE_LOG" || { say "not ready: the live reranker or the probe search is not as declared"; return 1; }
  k=1; while [ -e "$RUNS/control-$k" ]; do k=$((k + 1)); done
  t0=$(date +%s)
  measure memory-retrieval visible "$RUNS/control-$k"; rc=$?
  say "control-$k: the measure's exit $rc; $(( $(date +%s) - t0 )) s"
  { [ $rc = 0 ] && check control "$RUNS/control-$k"; } || { say "not ready: the control failed"; return 1; }
  check families --sets-root "$ROOT" --clone "$CLONE" || { say "not ready: the families line is not item 5's"; return 1; }
  check declared --sets-root "$ROOT" --repo "$REPO" || { say "not ready: the set's digest is not the declaration's"; return 1; }
}

n=$( { [ "$RESTART" = 1 ] && [ "$ATTEMPTS" != 0 ]; } && echo 2 || echo 1)
if ! ready; then
  if [ $n = 1 ] && [ ! -e "$USED" ]; then say "STOP: not ready before the first search: the 80 is not touched; fix, then start again"
  else say "STOP: not ready before the restart: no restart into the same outage; nothing spent; to the owner (--restart once the servers are back)"; fi
  exit 1
fi

# ---- 5. USED, before the first search
if [ ! -e "$USED" ]; then
  ( set -C; printf 'used %s by run_measure.sh (pid %s)\n' "$(date '+%F %T')" "$$" > "$USED" ) 2>/dev/null \
    || { say "STOP: USED could not be written new (another run?): the 80 is not touched"; exit 1; }
  say "USED written: the fresh 80 is used from now on"
fi

# ---- 6, 7. the attempts and the fault rule
fault() { echo "$2" > "$RUNS/$1/FAULT"; say "FAULT in $1: $2 (its partial outputs are kept, never the verdict)"; }
while :; do
  CUR=attempt-$n; t0=$(date +%s)
  say "== $(date '+%F %T') $CUR: memory-verdict-2 --part hidden"
  measure memory-verdict-2 hidden "$RUNS/$CUR"; rc=$?
  [ $rc = 9 ] && { say "STOP: $CUR exists already: never a restart into the same folder"; CUR=""; exit 1; }
  date '+%F %T' > "$RUNS/$CUR/ENDED"
  ST1=$(check store --clone "$CLONE")
  say "$CUR: the measure's exit $rc; $(( $(date +%s) - t0 )) s; median call $(median "$RUNS/$CUR/ms") ms"
  if [ "$ST1" != "$ST0" ]; then
    fault "$CUR" "the clone's store changed during the run (sha256 ${ST0:0:16} -> ${ST1:0:16})"
    echo "the store changed during $CUR" > "$RUNS/STOPPED"; say "STOP: the store changed: no restart on another store; to the owner"; CUR=""; break
  fi
  if [ $rc = 0 ] && check attempt --sets-root "$ROOT" "$CUR"; then
    date '+%F %T' > "$RUNS/$CUR/DONE"; echo "$CUR" > "$COUNTS"; say "$CUR counts (COUNTS)"; CUR=""; break
  fi
  fault "$CUR" "exit $rc, an output not whole, or a search answered otherwise than declared"
  if [ $n = 2 ]; then
    echo "a second fault ($CUR)" > "$RUNS/STOPPED"; say "STOP: a second fault: everything stops; to the owner (FRESH-80-1 §3.5)"; CUR=""; break
  fi
  CUR=""
  say "one restart, from the start, into a new folder, whatever the partial figures show (§3.5); first the live service and the control (review R1)"
  if ! ready; then
    say "STOP: not ready before the restart: no restart into the same outage; nothing spent; to the owner (--restart once the servers are back)"
    break
  fi
  n=2
done

# ---- 8. recorded after
INT1=$(git -C "$REPO" rev-parse refs/heads/w2/integrate 2>/dev/null || echo none)
IS1=$(wc -l < "$ISLOG" 2>/dev/null || echo 0)
say "integrate before ${INT0:0:12}, after ${INT1:0:12}: $([ "$INT0" = "$INT1" ] && echo unchanged || echo 'MOVED during the run: reported')"
say "the integration store log: $((IS1 - IS0)) new line(s) over the run window"
[ "$IS1" -gt "$IS0" ] && tail -n +$((IS0 + 1)) "$ISLOG" | head -20 | while IFS= read -r l; do say "  store log: $l"; done
k=1; while [ -e "$RUNS/record-$k.txt" ]; do k=$((k + 1)); done
{ echo "integrate_before $INT0"; echo "integrate_after $INT1"; echo "store_before $ST0"; echo "store_after $(check store --clone "$CLONE")"; echo "store_log_new_lines $((IS1 - IS0))"; } > "$RUNS/record-$k.txt"
if [ -e "$COUNTS" ]; then say "== $(date '+%F %T') done: $(cat "$COUNTS") counts; next: the judged reader run"; exit 0; fi
say "== $(date '+%F %T') stopped: no attempt counts"; exit 1
