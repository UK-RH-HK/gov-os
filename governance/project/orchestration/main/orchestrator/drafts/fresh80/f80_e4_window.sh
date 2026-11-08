#!/usr/bin/env bash
# THE FRESH 80, DATA ONLY, NOT JUDGED (DEC-1097 (1)(c), (5)): E4's scoring window over the 80's candidates. Built by
# drafts/fresh80/make_f80_e4.py from drafts/score-once/e4_window.sh (its F1 restore fix kept); the list of changes is
# in make_f80_e4.py. Run after f80_e4_prep.sh, the hold ended:
#   DRY=1 bash f80_e4_window.sh --sets-root ~/gov-os-eval
#   setsid bash f80_e4_window.sh --sets-root ~/gov-os-eval [gte zer] > ~/gov-os-runs/fresh-80/e4-window.out 2>&1 &
# What follows is e4_window.sh's own text, changed only as the list says.
# E4's one quiet GPU window (E3-E5-DESIGN §1, E0B-RESULT "Next"): gte, then zerank, each score once every text of
# window 4's 138 that its kept scores lack (counted by e4_prep.sh), each into its own window cache (~/gov-os-runs/D4B/
# e4/caches/<m>: its seed plus E0b's route answers; never a kept cache). Built on score_once_window.sh's and
# extend_window.sh's frame, in live_window.sh's form: the live service stopped for the window and restored (class 3's
# start line) on EVERY exit path (one trap); one trial service at a time, started by setsid, its pid and group checked,
# READY on cuda; the backstop on this script's group, the service's and each measure's, armed from the first load, each
# new one checked alive before the old one stops; the harness stops at the budget (14,255 MiB); every stop by pid or
# group via tools/proc.sh (L-0075); between models the service stopped by group and the GPU back to the base (read with
# both embedders warm). Counts only.
#   setsid bash e4_window.sh [gte zer] > <file> 2>&1 &    (DRY=1: the conditions and the plan only; nothing stops or
#   starts). Run it in the background, its output to a file; stop it early only by TERM to its pid with a grace longer
#   than the cleanup: bash tools/proc.sh stop --grace 300 <pid>. A TERM or INT to its whole group, or its output
#   closing, still restores (review F1: the output frame and the cleanup ignore them); a SIGSTOP (the backstop's
#   pause) does not: the trap cannot run, and the live service stays down until it is restored by hand.
# Per model: its headroom checked (the base + its rise in the 11-06 window must stay under the budget), the service
# started on $TR/run, the GPU sampled, so_measure.sh's r80 then r60 (point e4-window; v456 + rq + lift_norm 0.0766,
# E0b B's variant; GOV_RX_POOL_OFF=1; GOV_RX_RERANK_DIR on the trial socket: the single-model trial path of the
# score-once and extend windows), the service stopped by group, back to the base; then, with no GPU, the checks: no
# new route answer (the candidate lists are E0b's), and every text the count found the replays will ask now held
# (e4_count.py --check: 0 lacking). Any check not met stops the window; the trap restores.
# The 0.6B (M1's other model) is not scored here: the count found its texts in E0b's seed and run A's own cache.
# The GPU slots (rerank_worker.take_slot; DEC-1036 T6): one trial service at a time, at the default
# GOV_RERANK_GPU_SLOTS=2, as the score-once and extend windows ran: the live stop frees its slot, the slot-hold watcher
# (tools/rerank_service_slot_hold.py --watch) keeps the other or frees it after 60 s with no service; the trial service
# takes a free one; a private reranker finds none while a service runs.
# This file has no test seam: test_e4.py runs a temporary copy with one stubs line added before the OUT line below, and
# checks that the copy less that line is this file, byte for byte.
set -uo pipefail
unset GOV_RERANK_GPU_SLOT
for v in $(compgen -e); do case "$v" in GOV_RX*|E4_*) unset "$v";; esac; done
R=/home/usain/Dynamic-Agentic-Engineering-OS; O=$R/.gov-runtime/scratch/orchestrator; S=$O/drafts/score-once
D=$O/drafts/d4b; P=$HOME/gov-os-runs/D4B; CLONE=$P/w4-e0/repo; COMMIT=c00d525fd420
SETS_ROOT=""; MODELS=()
while [ $# -gt 0 ]; do case "$1" in --sets-root) SETS_ROOT=${2:-}; shift 2 || exit 2;; --sets-root=*) SETS_ROOT=${1#*=}; shift;; *) MODELS+=("$1"); shift;; esac; done
[ ${#MODELS[@]} -gt 0 ] || MODELS=(gte zer)
ROOT=$(realpath -e "$SETS_ROOT" 2>/dev/null) || { echo "STOP: --sets-root <root> is required"; exit 2; }
RUNS=$ROOT/runs/fresh-80; F=$O/drafts/fresh80
Q=$RUNS/data/e4; QC=$Q/caches; CNT=$Q/count; POINT=trial
V=~/.local/share/gov-os/reranker-trial-venv; TR=~/.local/share/gov-os/rerank-trial; C=~/.cache/gov-os-trial; RUN=$TR/run
VARIANT='{"sem_uncut":true,"sem_k":60,"lex_k":60,"depth":40,"perfile":2,"dedup":true,"rq":"question","lift_norm":0.0766}'
BUDGET=14255; BASE_TRIES=60; BASE_EVERY=5; LOAD_WAIT_S=300; MARGIN=300
LIVE_LOG=~/.cache/gov-os/rerank.log
# (the models: parsed above, with --sets-root)
declare -A ID REV HFH LOADER BATCH CHARS MCUT RISE
ID[gte]=Alibaba-NLP/gte-reranker-modernbert-base; REV[gte]=f7481e6055501a30fb19d090657df9ec1f79ab2c; HFH[gte]=$C/hf
ID[zer]=zeroentropy/zerank-1-small-reranker;      REV[zer]=a65fd51c450e9b47fdddab98e31166ecad21af8d; HFH[zer]=$C/hf; LOADER[zer]=yes-logit; MCUT[zer]=10000
# the rise over the base in the 11-06 score-once window (window.log: peak during its runs less the base 6,096 MiB)
RISE[gte]=1563; RISE[zer]=6220
LIVE_STOPPED=0; SVC=""; SP=""; BS=""; SAMP=""; HELD=0; MP=""; MG=""; BASE=""; OUT=""; STUCK=""

# ---- the machine: the GPU, the embedders, the live service, the hold, the backstop, the stops
gpu() { nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits | head -1; }
gpu_total() { nvidia-smi --query-gpu=memory.total --format=csv,noheader,nounits | head -1; }
warm() {  # page both embedders in, so a base or a return-to-base reading is not low by Windows' paging
  curl -s -m 60 http://127.0.0.1:11434/api/embed -d '{"model":"qwen3-embedding:0.6b","input":"warm"}' > /dev/null
  curl -s -m 60 http://127.0.0.1:11435/api/embed -d '{"model":"qwen3-embedding:0.6b","input":"warm"}' > /dev/null
  sleep 5
}
start_sampler() {  # start_sampler <file>: nvidia-smi at 1 Hz into the file; its pid into SAMP
  nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits -lms 1000 > "$1" & SAMP=$!
}
stop_sampler() { [ -n "$SAMP" ] && kill "$SAMP" 2>/dev/null; SAMP=""; }
restore() {  # class 3's start line. Run from the cleanup, which ignores INT, TERM and PIPE (review F1): each gov call
  # runs in its own session (setsid -w: a second signal to this group cannot cut it short) with those signals back to
  # their defaults (env --default-signal), so the live service it starts does not inherit the cleanup's ignores
  ( cd /home/usain/gov-os-worktrees/W2-00-store && GOV_RERANK_IDLE_S=43200 setsid -w env --default-signal=INT,TERM,PIPE ~/.local/bin/gov retrieve "what decides a close" --json > /dev/null 2>&1 )
  by=$(cd /home/usain/gov-os-worktrees/W2-00-store && setsid -w env --default-signal=INT,TERM,PIPE ~/.local/bin/gov retrieve "what decides a close" --json 2>/dev/null | python3 -c "import json,sys; print((json.load(sys.stdin)['result'].get('rerank') or {}).get('by'))")
  echo "restore: $(tail -1 $LIVE_LOG); class 3's check: rerank.by = $by; GPU $(gpu) MiB"
  printf '{"at": "%s", "class": 3, "reason": "the fresh 80 E4 scoring window ended (data only, DEC-1097 (1)(c))", "check": "rerank.by %s"}\n' "$(date '+%F %T')" "$by" >> $O/log/restarts.jsonl
}
take_hold() {
  printf 'E4-WINDOW ON THE FRESH 80 (data only): the CTO'"'"'s own hold for the E4 scoring window, from %s\n' "$(date '+%F %T')" > $O/log/act-in-progress.txt; HELD=1
}
release_hold() {
  [ "$HELD" = 1 ] && [ -e $O/log/act-in-progress.txt ] && mv $O/log/act-in-progress.txt $O/log/act-in-progress.ended-$(date +%H%M)-e4-window.txt
  HELD=0
}
stop_live() {  # the live service, by the pid its READY line names, after its cmdline is checked
  local lp
  lp=$(grep READY $LIVE_LOG | tail -1 | grep -oE 'pid [0-9]+' | awk '{print $2}')
  LIVE_STOPPED=1
  if [ -n "$lp" ] && tr '\0' ' ' < /proc/$lp/cmdline 2>/dev/null | grep -q 'gov/retrieval/rerank_service.py'; then
    bash $O/tools/proc.sh stop --grace 30 "$lp" || stop "the live service did not stop"
  fi
}
stop_group() { bash $O/tools/proc.sh stop --grace "$2" "$1"; }  # stop_group <pid|-pgid> <grace s>
disarm() { [ -n "$BS" ] && bash $O/tools/proc.sh stop --grace 5 "$BS" > /dev/null 2>&1; BS=""; }
alive_pid() { kill -0 "$1" 2>/dev/null && [ "$(ps -o stat= -p "$1" 2>/dev/null | cut -c1)" != Z ]; }
arm() {  # the backstop on the groups given; the new one up and checked alive after a second before the old one stops;
  # one that exits at once (a bad argument) stops the window, the old one still guarding until the trap has stopped all
  local old=$BS
  setsid bash $O/tools/gpu_backstop.sh "$@" < /dev/null > /dev/null 2>&1 & BS=$!
  sleep 1
  if ! alive_pid "$BS"; then
    BS=$old
    stop "the backstop on groups $* did not stay up: the run is not left unguarded"
  fi
  [ -n "$old" ] && bash $O/tools/proc.sh stop --grace 5 "$old" > /dev/null 2>&1
  echo "backstop pid $BS on groups $*"
}
stop_services() {  # by group, the measure first; each one once. A trial service that survives SIGKILL is remembered
  # (STUCK, review F3): the window then stops, and the cleanup does not restore over it
  [ -n "$MP" ] && { echo "stopping the measure's group $MP"; stop_group "-$MP" 10; }; MP=""
  if [ -n "$SVC" ]; then
    echo "stopping the trial service, group ${SVC#-}"
    stop_group "$SVC" 30 || STUCK="the trial service's group ${SVC#-} survived SIGKILL"
  fi
  SVC=""; SP=""
}
stuck_hold() {  # the hold stays, rewritten to say why: the live service is left down on purpose
  printf 'E4-WINDOW NOT RESTORED (%s): %s; the live service was NOT restored (it would share the GPU with it). Free the GPU, then class 3'"'"'s start line by hand.\n' "$(date '+%F %T')" "$STUCK" > $O/log/act-in-progress.txt
}

# ---- the caches and the counts (no GPU)
scores_in() { python3 -c "import sqlite3, sys; print(sqlite3.connect(f'file:{sys.argv[1]}/cache.db?mode=ro', uri=True).execute('SELECT COUNT(*) FROM score').fetchone()[0])" "$1"; }
routes_in() { python3 -c "import sqlite3, sys; print(sqlite3.connect(f'file:{sys.argv[1]}/cache.db?mode=ro', uri=True).execute('SELECT COUNT(*) FROM memo').fetchone()[0])" "$1"; }
cache_ok() { python3 "$S/e4_prepare.py" check "$QC/$1" "$CLONE" "${ID[$1]}@${REV[$1]}"; }  # cache_ok <model>
lacking() { python3 "$S/e4_count.py" --check "$CNT" "$1" "$QC/$1"; }  # lacking <model>: exit 0 when none lacks
figures() { echo "$1 alone on the 80 (the window's trial run): question lines $(grep -c ' (hidden): hit@5 ' "$Q/$POINT/$1/measure.txt")"; }

# ---- the conditions and the plan
stop() { echo "STOP: $*"; exit 1; }
NOTMET=0
need() {  # need "<condition>" <command ...>: DRY lists every condition; a real run stops at the first not met
  local what=$1; shift
  if "$@"; then echo "ok:      $what"; else echo "NOT MET: $what"; NOTMET=$((NOTMET + 1)); [ "${DRY:-0}" = 1 ] || stop "$what"; fi
}
PINNED=(rx.py so_measure.sh seed_scores.py rerank_worker.py e4_prep.sh e4_prepare.py e4_count.py e4_window.sh e4_replays.sh)
pinned() {  # every file listed in the pin, and each as reviewed
  local f
  for f in "${PINNED[@]}"; do grep -qE "^[0-9a-f]{64}  $f\$" "$S/E4-REVIEWED.sha256" 2>/dev/null || return 1; done
  ( cd "$S" && sha256sum --quiet -c E4-REVIEWED.sha256 ) || return 1
  [ -s "$F/FRESH80-REVIEWED.sha256" ] && ( cd "$F" && sha256sum --quiet -c FRESH80-REVIEWED.sha256 )
}
quietly() { "$@" > /dev/null 2>&1; }  # a condition whose own line the need line already shows (review F7)
numeric() { [[ "$1" =~ ^[0-9]+$ ]]; }  # an empty or garbled nvidia-smi reading is a failed check, never 0 (review F2)
snapshot() { [ -d "${HFH[$1]}/hub/models--${ID[$1]//\//--}/snapshots/${REV[$1]}" ]; }
lock_free() { [ ! -e "$1" ] || flock -n "$1" true; }
quiet() { grep -q "heavy slots held: none" $O/dispatch/status.txt && grep -q "^Jobs by phase: none" $O/dispatch/status.txt; }
no_act() { [ ! -e $O/log/act-in-progress.txt ]; }
at_commit() { [ "$(git -C "$CLONE" rev-parse --short=12 HEAD 2>/dev/null)" = "$COMMIT" ]; }
counted() { [ -s "$CNT/need-$1.txt" ] && [ -s "$CNT/v80/measure.txt" ]; }
slots_free() { local i n=0; for i in 0 1; do lock_free /tmp/gov-os-rerank-gpu-$i.lock && n=$((n + 1)); done; echo $n; }
conditions() {
  local m
  need "the reviewed E4 files ($S/E4-REVIEWED.sha256: rx.py, so_measure.sh, seed_scores.py, rerank_worker.py, e4_prep.sh, e4_prepare.py, e4_count.py, e4_window.sh, e4_replays.sh)" \
    pinned
  need "the trial service's worker is the reviewed score-once copy" cmp -s $S/rerank_worker.py $TR/svc/rerank_worker.py
  need "the trial service and its venv" test -f "$TR/svc/rerank_service.py" -a -x "$V/bin/python"
  for m in "${MODELS[@]}"; do
    need "$m is gte or zer" test -n "${ID[$m]:-}"
    [ -n "${ID[$m]:-}" ] || continue
    need "$m's snapshot ${ID[$m]}@${REV[$m]:0:8} under ${HFH[$m]}" snapshot "$m"
    need "$m's window cache: its model alone, keyed by the clone's store now, E0b's route answers ($(cache_ok "$m" 2>&1 | tail -1))" quietly cache_ok "$m"
    need "$m counted by e4_prep.sh ($CNT; now: $(lacking "$m" 2>&1 | tail -1))" counted "$m"
  done
  need "the measure clone at $COMMIT" at_commit
  need "quiet (the dispatcher: no heavy slot held, no job)" quiet
  need "no ACT in progress" no_act
  need "the trial lock free ($RUN/rerank.lock)" lock_free "$RUN/rerank.lock"
  need "the measure and the stop and backstop tools" test -f $F/f80_so_measure.sh -a -f $O/tools/proc.sh -a -f $O/tools/gpu_backstop.sh
  need "GOV_STORE unset (reviewer 1 S6)" test -z "${GOV_STORE+x}"
  need "the fresh 80's hold has ended" eval '! grep -q "FRESH-80 HOLD" $O/log/act-in-progress.txt 2>/dev/null'
  echo "note:    GPU reranker slots now $(slots_free) of 2 free; the live service's comes free at its stop, and one free slot is checked after it (else the window stops and restores)"
  [ -e "$RUN/rerank.sock" ] && echo "note:    a socket at $RUN/rerank.sock with its lock free is stale; it is removed before the start"
  echo "GPU now $(gpu) of $(gpu_total) MiB (the live service up); the budget $BUDGET MiB"
}
embedders() {
  need "the shared embedder answers (:11434)" curl -s -m 10 -o /dev/null http://127.0.0.1:11434/api/version
  need "the query embedder answers (:11435)" curl -s -m 10 -o /dev/null http://127.0.0.1:11435/api/version
}
plan() {
  local m
  echo "plan: hold taken; the live service stopped (class 3); both embedders warmed; the base read; a free slot checked"
  for m in "${MODELS[@]}"; do
    echo "plan $m: ${ID[$m]}@${REV[$m]} HF_HOME=${HFH[$m]} loader=${LOADER[$m]:-cross-encoder} on $RUN; bounds ${BATCH[$m]:-16} texts, ${CHARS[$m]:-24000} chars; model cut ${MCUT[$m]:-0}"
    echo "  headroom first: the GPU read just before the load (a number, else a stop) + ${RISE[$m]} MiB (its 11-06 rise) + $MARGIN must stay under $BUDGET, and a slot free, else the window stops before the load"
    echo "  setsid, GOV_RERANK_TRIAL_RELEASE=1 GOV_RERANK_IDLE_S=3600 HF_HUB_OFFLINE=1; READY on cuda within $LOAD_WAIT_S s, pid = group checked; the backstop re-armed on its group"
    echo "  f80_so_measure.sh $POINT $m (the 80, v80): variant $VARIANT; CLONE=$CLONE GOV_RX_POOL_OFF=1 GOV_RX_RERANK_DIR=$RUN GOV_RX_RERANK_MODEL=${ID[$m]}@${REV[$m]} GOV_RX_GPU_LIMIT_MIB=$BUDGET; cache $QC/$m; each measure in its own group under the backstop"
    echo "  then the service stopped by group, the GPU back to the base + $MARGIN MiB within $((BASE_TRIES * BASE_EVERY)) s (else the window stops)"
    echo "  checks (no GPU): route answers unchanged; e4_count.py --check $CNT $m $QC/$m: 0 lacking; texts newly scored; figures (e0_figures.py)"
  done
  echo "the 0.6B (M1): none scored here (the count: its texts are in E0b's seed and run A's own cache)"
  echo "after the window, no GPU: bash $F/f80_e4_replays.sh --sets-root <root> (M3 = zer + gte merged, M1 = q06 + gte merged; strict replays)"
  echo "outputs: $Q/window/<stamp>/window.log; $Q/$POINT/<m>/; gpu-<m>.txt; the caches $QC/<m>"
}

# ---- one model
start_svc() {  # start_svc <model>: sets SP/SVC as soon as it starts
  local m=$1 n t0 st sp
  mkdir -p "$RUN"; chmod 700 "$RUN"
  flock -n "$RUN/rerank.lock" true || { echo "$m: the lock $RUN/rerank.lock is held"; return 1; }
  [ -e "$RUN/rerank.sock" ] && { echo "$m: a stale socket at $RUN/rerank.sock (its lock free): removed"; rm -f "$RUN/rerank.sock"; }
  touch "$RUN/rerank.log" "$RUN/service.log"
  n=$(wc -l < "$RUN/rerank.log")
  t0=$(date +%s.%N)
  ( exec 9>"$RUN/rerank.lock"; flock -n 9 || exit 1
    HF_HOME=${HFH[$m]} HF_HUB_OFFLINE=1 GOV_RERANK_IDLE_S=3600 GOV_RERANK_TRIAL_8BIT=0 \
      GOV_RERANK_TRIAL_LOADER=${LOADER[$m]:-} GOV_RERANK_TRIAL_RELEASE=1 \
      setsid "$V/bin/python" -I "$TR/svc/rerank_service.py" "${ID[$m]}" "${REV[$m]}" "$RUN/rerank.sock" 9 >> "$RUN/service.log" 2>&1 < /dev/null &
    echo $! > "$OUT/svc-$m.pid" ) || { echo "$m: the trial service did not start (its lock is held)"; return 1; }
  sp=$(cat "$OUT/svc-$m.pid"); SP=$sp; SVC="-$sp"  # its own group from the start: a slow load is stopped by it
  arm "$MG" "$SP"
  for i in $(seq 1 $LOAD_WAIT_S); do tail -n +$((n+1)) "$RUN/rerank.log" | grep -qE 'READY|REFUSED|END' && break; sleep 1; done
  st=$(tail -n +$((n+1)) "$RUN/rerank.log" | grep -E 'READY|REFUSED|END' | head -1)
  echo "$m load: $(echo "$(date +%s.%N) - $t0" | bc) s; $st; group $sp; GPU $(gpu) MiB (base $BASE)"
  case "$st" in *READY*cuda*) ;; *) tail -5 "$RUN/service.log"; echo "$m did not load on the GPU within $LOAD_WAIT_S s"; return 1;; esac
  [ "$(bash $O/tools/proc.sh pgid "$sp")" = "$sp" ] || { echo "$m: the service's process group is not its own pid $sp"; return 1; }
  case "$st" in *"pid $sp "*) ;; *) echo "$m: the READY line names another pid than the service's $sp"; return 1;; esac
}
measure() {  # measure <model> <set>: so_measure.sh in its own group (setsid), the backstop on it too
  local m=$1 rc
  CLONE=$CLONE GOV_RX_POOL_OFF=1 GOV_RX_RERANK_DIR=$RUN GOV_RX_RERANK_MODEL="${ID[$m]}@${REV[$m]}" GOV_RX_GPU_LIMIT_MIB=$BUDGET \
    GOV_RX_BATCH=${BATCH[$m]:-16} GOV_RX_REQUEST_CHARS=${CHARS[$m]:-24000} GOV_RX_MODEL_CUT=${MCUT[$m]:-0} \
    setsid bash "$F/f80_so_measure.sh" "$ROOT" "$POINT" "$m" "$VARIANT" "$QC/$m" < /dev/null & MP=$!
  arm "$MG" "$SP" "$MP"
  wait $MP; rc=$?; MP=""
  arm "$MG" "$SP"
  return $rc
}
run_model() {  # the GPU part of one model: headroom, load, the two measures, the stop, back to the base
  local m=$1 rc=0 set now
  echo "== $(date '+%F %T') $m: ${ID[$m]}@${REV[$m]}"
  now=$(gpu)  # review F2: the GPU read just before each load, not the window's first base
  numeric "$now" || stop "$m: the GPU reading before the load is not a number ('$now'): not loaded"
  [ $((now + ${RISE[$m]} + MARGIN)) -lt $BUDGET ] || stop "$m: the GPU now $now + its rise ${RISE[$m]} + $MARGIN reaches the budget $BUDGET: not loaded"
  [ "$(slots_free)" -ge 1 ] || stop "$m: no GPU reranker slot free (slots 0-1): not loaded"
  echo "$m: headroom $now + ${RISE[$m]} + $MARGIN < $BUDGET; a slot free"
  start_svc "$m" || stop "$m: the trial service did not come up"
  start_sampler "$OUT/gpu-$m.txt"
  for set in v80; do
    measure "$m" "$set" || { rc=1; echo "$m: the $set measure ended with an error"; break; }
  done
  stop_sampler
  [ -s "$OUT/gpu-$m.txt" ] && echo "$m: GPU peak during its runs $(sort -n "$OUT/gpu-$m.txt" | tail -1) MiB; samples at or above $BUDGET: $(awk -v b=$BUDGET '$1 >= b' "$OUT/gpu-$m.txt" | wc -l)"
  stop_services
  [ -z "$STUCK" ] || stop "$STUCK"
  disarm
  [ $rc = 0 ] || stop "$m's runs failed (see $Q/$POINT/measure.log)"
  warm
  for i in $(seq 1 $BASE_TRIES); do [ "$(gpu)" -le $((BASE + MARGIN)) ] && break; sleep "$BASE_EVERY"; done
  echo "$m: GPU after the stop $(gpu) MiB (base $BASE)"
  [ "$(gpu)" -le $((BASE + MARGIN)) ] || stop "the GPU did not return to the base after $m"
}
check_model() {  # no GPU: the candidate lists unchanged, nothing lacking now, the counts
  local m=$1 s1 r1
  s1=$(scores_in "$QC/$m"); r1=$(routes_in "$QC/$m")
  echo "$m: texts newly scored $((s1 - S0[$m])) (cache ${S0[$m]} -> $s1); route answers ${R0[$m]} -> $r1"
  [ "$r1" = "${R0[$m]}" ] || stop "$m: the trial runs asked the routes anew (${R0[$m]} -> $r1 route answers): the candidate lists may not be E0b's"
  lacking "$m" || stop "$m still lacks texts the replays will ask"
  figures "$m"
}
cleanup() {  # every exit path, once: the sampler, the measure, the service, the backstop, the live service, the hold.
  # Its first line ignores INT, TERM and PIPE (review F1): a second signal, or an output gone away, cannot cut the
  # restore short (a write to a dead output then fails without killing the script)
  rc=$?; trap '' INT TERM PIPE; trap - EXIT
  stop_sampler
  stop_services
  disarm
  if [ -n "$STUCK" ]; then  # review F3: never restore beside a trial service that survived SIGKILL
    echo "NOT RESTORED: $STUCK; the live service is left down (it would fight it for the GPU); the hold stays, rewritten. Free the GPU, then run class 3's start line by hand."
    stuck_hold
  else
    [ "$LIVE_STOPPED" = 1 ] && restore
    release_hold
  fi
  echo "== $(date '+%F %T') the E4 window ends (exit $rc)"
  exit $rc
}

# the output frame (review F1): tee ignores INT and TERM, so a signal to this whole group leaves it writing the log,
# and -p keeps it writing the log when the caller's output closes; the script's own writes then go on to the log
if [ "${DRY:-0}" != 1 ]; then OUT=$Q/window/$(date +%Y%m%d-%H%M%S); mkdir -p "$OUT"; exec > >(trap '' INT TERM; tee -p -a "$OUT/window.log" | sed -u "s#$RUNS#<run folder>#g; s#$ROOT#<sets root>#g") 2>&1; else exec > >(sed -u "s#$RUNS#<run folder>#g; s#$ROOT#<sets root>#g") 2>&1; fi
trap cleanup EXIT; trap 'exit 130' INT; trap 'exit 143' TERM

echo "== $(date '+%F %T') E4 scoring window: ${MODELS[*]} (DRY=${DRY:-0})"
conditions
if [ "${DRY:-0}" = 1 ]; then
  plan
  echo "DRY: $NOTMET condition(s) not met; nothing stopped or started"
  exit 0
fi
embedders
declare -A S0 R0
for m in "${MODELS[@]}"; do S0[$m]=$(scores_in "$QC/$m"); R0[$m]=$(routes_in "$QC/$m"); done
take_hold
stop_live
warm; BASE=$(gpu); echo "base GPU (the live service stopped, both embedders warm): $BASE MiB"
numeric "$BASE" || stop "the base GPU reading is not a number ('$BASE')"
[ "$(slots_free)" -ge 1 ] || stop "no GPU reranker slot free (slots 0-1) for the trial service"
MG=$(ps -o pgid= -p $$ | tr -d ' ')
for m in "${MODELS[@]}"; do
  run_model "$m"
  check_model "$m"
done
echo "== all models scored once; next, with no GPU: bash $F/f80_e4_replays.sh --sets-root <root>"
