#!/usr/bin/env bash
# D4B-SCORE-ONCE §4's real window for the two-model cells, as they would run: both models loaded, each search scored
# by both, merged (min-max, equal weights). M2 = the 4B (8-bit) + gte; M3 = zerank-1-small (yes-logit) + gte. Built
# on score_once_window.sh's safety frame: the live service stopped for the window and restored (class 3's start line)
# on EVERY exit path (one trap); each trial service started by setsid, its pid and group checked; the backstop on
# this script's group, both services' groups and the measure's, armed from the first load; the harness stops at the
# budget (14,255 MiB); every stop by pid or group (L-0075); between cells both services stopped by group and the GPU
# back to the base (read with both embedders warm). Counts and seconds only.
#   setsid bash live_window.sh [M2 M3]      (DRY=1: the conditions and the plan only; nothing stops or starts)
# Per cell, in this order: both loads (gte first), the GPU sampled into gpu-load.txt from the first load (reported as
# the load peak, not judged); the GPU after both loads (gpu-after-loads-raw); a warm-up, one short text to each
# service through its own socket (live_probe.py warm: the trial worker releases its cache after a request), then the
# GPU after the warm-up (gpu-after-warmup, the steady state); the judged sampler (gpu.txt) from here to the end of the
# 10 at once; the probe's peak against each socket at that model's own request bound; 20 searches alone (the first
# calls of the first 20 visible questions, live_searches.py, L3's variant), their median and p90; 10 at once, their
# median, slowest, failed, timed out and unranked. Then both services stopped by group, back to the base, the next
# cell. The trap judges every cell whose folder exists (live_verdict.py, §4's four lines) on every exit path, after
# the services stop and before the live service is restored. PAR=1 asks the two services at once in each search
# (GOV_RX_LIVE_PARALLEL); default one, then two.
# The GPU slots (rerank_worker.take_slot; DEC-1036 T6): the slot-hold watcher (tools/rerank_service_slot_hold.py
# --watch, slots 0-1) holds every slot of the two a running rerank_service.py does not, trial ones included; so with
# the default GOV_RERANK_GPU_SLOTS=2 the second trial service finds no slot and ends (exit 75, REFUSED). Both trial
# services here get GOV_RERANK_GPU_SLOTS=3: the first takes slot 0 (freed by the live stop), the second slot 2, the
# watcher keeps slot 1, and a private reranker (slots 0-1 only) still finds none. gte starts first: each start needs
# 5.5 GiB (5,632 MiB) free (rerank_service.gpu_short); after the 4B's load (10,736 MiB of the card's 16,303 in the
# 11-06 window) 5,567 would be left, so the second start would be refused (exit 77); after gte's (6,957), 9,346.
# This file has no test seam: test_live_window.py runs a temporary copy with one stubs line added before the OUT
# line below, and checks that the copy less that line is this file, byte for byte.
set -uo pipefail
unset GOV_RERANK_GPU_SLOT
for v in $(compgen -e); do case "$v" in GOV_RX*) unset "$v";; esac; done
R=/home/usain/Dynamic-Agentic-Engineering-OS; O=$R/.gov-runtime/scratch/orchestrator; S=$O/drafts/score-once
P=$HOME/gov-os-runs/D4B; CLONE=$P/g1/repo; QDIR=$CLONE/fixtures/evaluation/memory-retrieval/visible
V=~/.local/share/gov-os/reranker-trial-venv; TR=~/.local/share/gov-os/rerank-trial; C=~/.cache/gov-os-trial
RUN1=$TR/run; RUN2=$TR/run2
VARIANT='{"sem_uncut":true,"sem_k":60,"lex_k":60,"depth":40,"perfile":2,"dedup":true,"rq":"question","lift_norm":0.0766}'
RULE='{"kind":"merge","a":"one","b":"two"}'
BUDGET=14255; SLOTS=3; N_ALONE=20; N_ONCE=10
BASE_TRIES=60; BASE_EVERY=5; WARM_SETTLE_S=2; LOAD_WAIT_S=300
LIVE_LOG=~/.cache/gov-os/rerank.log
if [ $# -gt 0 ]; then CELLS=("$@"); else CELLS=(M2 M3); fi
declare -A ID REV HFH BIT LOADER BATCH CHARS MCUT ONE TWO
ID[q4b]=Qwen/Qwen3-Reranker-4B;                   REV[q4b]=22e683669bc0f0bd69640a1354a6d0aebcfeede5; HFH[q4b]=$C/hf; BIT[q4b]=1; BATCH[q4b]=8; CHARS[q4b]=12000
ID[gte]=Alibaba-NLP/gte-reranker-modernbert-base; REV[gte]=f7481e6055501a30fb19d090657df9ec1f79ab2c; HFH[gte]=$C/hf
ID[zer]=zeroentropy/zerank-1-small-reranker;      REV[zer]=a65fd51c450e9b47fdddab98e31166ecad21af8d; HFH[zer]=$C/hf; LOADER[zer]=yes-logit; MCUT[zer]=10000
ONE[M2]=q4b; TWO[M2]=gte
ONE[M3]=zer; TWO[M3]=gte
LIVE_STOPPED=0; SVC1=""; SVC2=""; SP1=""; SP2=""; BS=""; SAMP=""; LOADSAMP=""; HELD=0; MP=""; MG=""; CUR=""; OUT=""

# ---- the machine: the GPU, the embedders, the live service, the hold, the backstop, the stops
gpu() { nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits | head -1; }
gpu_total() { nvidia-smi --query-gpu=memory.total --format=csv,noheader,nounits | head -1; }
warm() {  # page both embedders in, so a base or a return-to-base reading is not low by Windows' paging
  curl -s -m 60 http://127.0.0.1:11434/api/embed -d '{"model":"qwen3-embedding:0.6b","input":"warm"}' > /dev/null
  curl -s -m 60 http://127.0.0.1:11435/api/embed -d '{"model":"qwen3-embedding:0.6b","input":"warm"}' > /dev/null
  sleep 5
}
start_sampler() {  # start_sampler <file> <variable>: nvidia-smi at 1 Hz into the file; its pid into the variable
  nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits -lms 1000 > "$1" & printf -v "$2" %s "$!"
}
stop_sampler() { local p=${!1}; [ -n "$p" ] && kill "$p" 2>/dev/null; printf -v "$1" %s ""; }
restore() {
  ( cd /home/usain/gov-os-worktrees/W2-00-store && GOV_RERANK_IDLE_S=43200 ~/.local/bin/gov retrieve "what decides a close" --json > /dev/null 2>&1 )
  by=$(cd /home/usain/gov-os-worktrees/W2-00-store && ~/.local/bin/gov retrieve "what decides a close" --json 2>/dev/null | python3 -c "import json,sys; print((json.load(sys.stdin)['result'].get('rerank') or {}).get('by'))")
  echo "restore: $(tail -1 $LIVE_LOG); class 3's check: rerank.by = $by; GPU $(gpu) MiB"
  printf '{"at": "%s", "class": 3, "reason": "the live two-model window ended (D4B-SCORE-ONCE §4)", "check": "rerank.by %s"}\n' "$(date '+%F %T')" "$by" >> $O/log/restarts.jsonl
}
take_hold() {
  printf 'LIVE-WINDOW (D4B-SCORE-ONCE §4): the CTO'"'"'s own hold for the live two-model window, from %s\n' "$(date '+%F %T')" > $O/log/act-in-progress.txt; HELD=1
}
release_hold() {
  [ "$HELD" = 1 ] && [ -e $O/log/act-in-progress.txt ] && mv $O/log/act-in-progress.txt $O/log/act-in-progress.ended-$(date +%H%M)-live-window.txt
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
arm() {  # the backstop on the groups given (this script's, the services', the measure's); the new one up and checked
  # alive after a second before the old one stops; one that exits at once (a bad argument) stops the window, the old
  # one still guarding until the trap has stopped everything
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
stop_services() {  # by group, the measure first; each one once
  [ -n "$MP" ] && { echo "stopping the measure's group $MP"; stop_group "-$MP" 10; }; MP=""
  [ -n "$SVC1" ] && { echo "stopping trial service one, group ${SVC1#-}"; stop_group "$SVC1" 30; }; SVC1=""
  [ -n "$SVC2" ] && { echo "stopping trial service two, group ${SVC2#-}"; stop_group "$SVC2" 30; }; SVC2=""
  SP1=""; SP2=""
}

# ---- the conditions and the plan
stop() { echo "STOP: $*"; exit 1; }
NOTMET=0
need() {  # need "<condition>" <command ...>: DRY lists every condition; a real run stops at the first not met
  local what=$1; shift
  if "$@"; then echo "ok:      $what"; else echo "NOT MET: $what"; NOTMET=$((NOTMET + 1)); [ "${DRY:-0}" = 1 ] || stop "$what"; fi
}
snapshot() { [ -d "${HFH[$1]}/hub/models--${ID[$1]//\//--}/snapshots/${REV[$1]}" ]; }
lock_free() { [ ! -e "$1" ] || flock -n "$1" true; }
quiet() { grep -q "heavy slots held: none" $O/dispatch/status.txt && grep -q "^Jobs by phase: none" $O/dispatch/status.txt; }
no_act() { [ ! -e $O/log/act-in-progress.txt ]; }
has_bnb() { "$V/bin/python" -I -c "import importlib.util, sys; sys.exit(importlib.util.find_spec('bitsandbytes') is None)"; }
twenty() { [ "$(ls "$QDIR"/*.yaml 2>/dev/null | wc -l)" -ge $N_ALONE ]; }
slots_free() { local i n=0; for i in $(seq 0 $((SLOTS - 1))); do lock_free /tmp/gov-os-rerank-gpu-$i.lock && n=$((n + 1)); done; echo $n; }
slot_states() { local i out=""; for i in $(seq 0 $((SLOTS - 1))); do lock_free /tmp/gov-os-rerank-gpu-$i.lock && out+=" $i:free" || out+=" $i:held"; done; echo "${out# }"; }
conditions() {
  local m d
  need "the reviewed live files ($S/LIVE-REVIEWED.sha256: rx.py, live_window.sh, live_searches.py, live_probe.py, live_verdict.py, rerank_worker.py)" \
    sha256sum --quiet -c "$S/LIVE-REVIEWED.sha256"
  need "the trial service's worker is the reviewed score-once copy" cmp -s $S/rerank_worker.py $TR/svc/rerank_worker.py
  need "the trial service and its venv" test -f "$TR/svc/rerank_service.py" -a -x "$V/bin/python"
  for m in $(printf '%s\n' "${MODELS[@]}" | sort -u); do need "$m's snapshot ${ID[$m]}@${REV[$m]:0:8} under ${HFH[$m]}" snapshot "$m"; done
  case " ${MODELS[*]} " in *" q4b "*) need "bitsandbytes in the trial venv (the 4B's 8-bit load)" has_bnb;; esac
  need "quiet (the dispatcher: no heavy slot held, no job)" quiet
  need "no ACT in progress" no_act
  need "trial lock one free ($RUN1/rerank.lock)" lock_free "$RUN1/rerank.lock"
  need "trial lock two free ($RUN2/rerank.lock$([ -d "$RUN2" ] || echo '; the folder is created, mode 700'))" lock_free "$RUN2/rerank.lock"
  need "$N_ALONE visible questions in the measure clone ($QDIR)" twenty
  need "the stop and backstop tools" test -f $O/tools/proc.sh -a -f $O/tools/gpu_backstop.sh
  need "GPU reranker slots for two trial services at GOV_RERANK_GPU_SLOTS=$SLOTS (now $(slot_states); the live service's comes free at its stop)" \
    test $(( $(slots_free) + 1 )) -ge 2
  for d in "$RUN1" "$RUN2"; do [ -e "$d/rerank.sock" ] && echo "note:    a socket at $d/rerank.sock with its lock free is stale; it is removed before the start"; done
  echo "the measure clone at $(git -C "$CLONE" rev-parse --short=12 HEAD); GPU now $(gpu) of $(gpu_total) MiB"
}
embedders() {
  need "the shared embedder answers (:11434)" curl -s -m 10 -o /dev/null http://127.0.0.1:11434/api/version
  need "the query embedder answers (:11435)" curl -s -m 10 -o /dev/null http://127.0.0.1:11435/api/version
}
slots_after_stop() {
  [ "$(slots_free)" -ge 2 ] || stop "only $(slots_free) of $SLOTS GPU reranker slots free ($(slot_states)): two trial services need two"
}
plan() {
  local c a b
  for c in "${CELLS[@]}"; do
    a=${ONE[$c]}; b=${TWO[$c]}
    echo "plan $c: rule $RULE"
    echo "  two = $b ${ID[$b]}@${REV[$b]} HF_HOME=${HFH[$b]} 8bit=${BIT[$b]:-0} loader=${LOADER[$b]:-cross-encoder} on $RUN2 (starts first: the smaller); bounds ${BATCH[$b]:-16} texts, ${CHARS[$b]:-24000} chars; model cut ${MCUT[$b]:-0}"
    echo "  one = $a ${ID[$a]}@${REV[$a]} HF_HOME=${HFH[$a]} 8bit=${BIT[$a]:-0} loader=${LOADER[$a]:-cross-encoder} on $RUN1; bounds ${BATCH[$a]:-16} texts, ${CHARS[$a]:-24000} chars; model cut ${MCUT[$a]:-0}"
    echo "  each service: setsid, GOV_RERANK_GPU_SLOTS=$SLOTS GOV_RERANK_TRIAL_RELEASE=1 GOV_RERANK_IDLE_S=3600 HF_HUB_OFFLINE=1; READY on cuda within ${LOAD_WAIT_S} s, pid = group checked; the backstop re-armed on each new group"
    echo "  the GPU sampled from the first load (gpu-load.txt: the load peak, reported only); the GPU after both loads (raw)"
    echo "  the warm-up: one short text to each service (live_probe.py warm), ${WARM_SETTLE_S} s, then the GPU after the warm-up; the judged sampler (gpu.txt) from here to the end of the $N_ONCE at once"
    echo "  probe peak --limit $BUDGET on each socket at its own bound (one: --bound ${CHARS[$a]:-24000} --max-texts ${BATCH[$a]:-16}; two: --bound ${CHARS[$b]:-24000} --max-texts ${BATCH[$b]:-16}); a shape at the budget or refused: no searches"
    echo "  $N_ALONE searches alone, then $N_ONCE at once: live_searches.py, variant $VARIANT, GOV_RX_GPU_LIMIT_MIB=$BUDGET, GOV_RERANK_TIMEOUT_S=30, GOV_RX_LIVE_PARALLEL=${PAR:-0}; each in its own group (setsid) under the backstop"
    echo "  then both services stopped by group, the GPU back to the base + 300 MiB within $((BASE_TRIES * BASE_EVERY)) s (else the window stops)"
  done
  echo "eligibility (§4, live_verdict.py, from the trap on every exit path), per cell: the full median search alone <= 3.0 s (the harness's GPU reads included; less them reported only) and none failed or unranked; no request timed out at $N_ONCE at once (30 s), none failed or unranked; no probe shape at the budget; no judged GPU sample at or above $BUDGET MiB (reported only: the load peak, and the GPU after the warm-up + each service's largest peak-reserved minus reserved-after)"
  echo "outputs: $P/live-window/<stamp>/ (window.log; per cell gpu-load.txt, gpu.txt, gpu-after-*.txt, warm-*.txt, probe-*.txt, alone/, once/, verdict.json)"
}

# ---- one cell
start_svc() {  # start_svc one|two <model> <folder> <cell folder>: sets SP1/SVC1 or SP2/SVC2 as soon as it starts
  local k=$1 m=$2 dir=$3 d=$4 n t0 st sp
  mkdir -p "$dir"; chmod 700 "$dir"
  flock -n "$dir/rerank.lock" true || { echo "$k: the lock $dir/rerank.lock is held"; return 1; }
  [ -e "$dir/rerank.sock" ] && { echo "$k: a stale socket at $dir/rerank.sock (its lock free): removed"; rm -f "$dir/rerank.sock"; }
  touch "$dir/rerank.log" "$dir/service.log"
  n=$(wc -l < "$dir/rerank.log"); wc -l < "$dir/service.log" > "$d/service-$k.from"
  t0=$(date +%s.%N)
  ( exec 9>"$dir/rerank.lock"; flock -n 9 || exit 1
    HF_HOME=${HFH[$m]} HF_HUB_OFFLINE=1 GOV_RERANK_IDLE_S=3600 GOV_RERANK_TRIAL_8BIT=${BIT[$m]:-0} \
      GOV_RERANK_TRIAL_LOADER=${LOADER[$m]:-} GOV_RERANK_TRIAL_RELEASE=1 GOV_RERANK_GPU_SLOTS=$SLOTS \
      setsid "$V/bin/python" -I "$TR/svc/rerank_service.py" "${ID[$m]}" "${REV[$m]}" "$dir/rerank.sock" 9 >> "$dir/service.log" 2>&1 < /dev/null &
    echo $! > "$d/svc-$k.pid" ) || { echo "$k: the trial service did not start (its lock is held)"; return 1; }
  sp=$(cat "$d/svc-$k.pid")
  if [ "$k" = one ]; then SP1=$sp; SVC1="-$sp"; else SP2=$sp; SVC2="-$sp"; fi  # its own group from the start
  arm "$MG" $SP2 $SP1
  for i in $(seq 1 $LOAD_WAIT_S); do tail -n +$((n+1)) "$dir/rerank.log" | grep -qE 'READY|REFUSED|END' && break; sleep 1; done
  st=$(tail -n +$((n+1)) "$dir/rerank.log" | grep -E 'READY|REFUSED|END' | head -1)
  echo "$k ($m) load: $(echo "$(date +%s.%N) - $t0" | bc) s; $st; group $sp; GPU $(gpu) MiB (base $BASE)"
  case "$st" in *READY*cuda*) ;; *) tail -5 "$dir/service.log"; echo "$k ($m) did not load on the GPU within $LOAD_WAIT_S s"; return 1;; esac
  [ "$(bash $O/tools/proc.sh pgid "$sp")" = "$sp" ] || { echo "$k: the service's process group is not its own pid $sp"; return 1; }
  case "$st" in *"pid $sp "*) ;; *) echo "$k: the READY line names another pid than the service's $sp"; return 1;; esac
}
warm_svc() { "$V/bin/python" -I "$S/live_probe.py" "$1" warm; }  # warm_svc <socket>
probe_svc() { "$V/bin/python" -I "$S/live_probe.py" "$1" peak --limit $BUDGET --bound "$2" --max-texts "$3"; }
searches() {  # searches alone|once <n> <cell folder>: in its own group (setsid), the backstop on it too
  local rc
  setsid python3 "$S/live_searches.py" "$1" "$2" --clone "$CLONE" --rx "$S/rx.py" --variant "$VARIANT" --out "$3/$1" \
    > "$3/$1.txt" 2>&1 < /dev/null & MP=$!
  arm "$MG" "$SP2" "$SP1" "$MP"
  wait $MP; rc=$?; MP=""
  return $rc
}
mark_to() {  # the end of this cell's lines in each service log (live_verdict.py reads from .from to .to)
  local k d=$OUT/$1 dir
  for k in one two; do
    [ $k = one ] && dir=$RUN1 || dir=$RUN2
    [ -s "$d/service-$k.from" ] && [ ! -e "$d/service-$k.to" ] && wc -l < "$dir/service.log" > "$d/service-$k.to"
  done
  return 0
}
verdicts() {  # §4's lines for every cell whose folder exists (from the trap, on every exit path)
  [ -n "$OUT" ] && [ -d "$OUT" ] || return 0
  echo "== $(date '+%F %T') eligibility (D4B-SCORE-ONCE §4)"
  python3 "$S/live_verdict.py" "$OUT" "$BUDGET" "$RUN1/service.log" "$RUN2/service.log" "${CELLS[@]}"
}

run_cell_body() {
  local c=$1 a=${ONE[$1]} b=${TWO[$1]} d=$OUT/$1 rc k m sock raw warmed ok=1 mode n
  mkdir -p "$d"
  echo "== $(date '+%F %T') $c: one = $a (${ID[$a]}), two = $b (${ID[$b]}); $RULE"
  start_sampler "$d/gpu-load.txt" LOADSAMP
  start_svc two "$b" "$RUN2" "$d" || return 1
  start_svc one "$a" "$RUN1" "$d" || return 1
  raw=$(gpu); echo "$raw" > "$d/gpu-after-loads-raw.txt"
  echo "$c: GPU after both loads, before the warm-up: $raw MiB (base $BASE)"
  for k in one two; do
    [ $k = one ] && sock=$RUN1/rerank.sock || sock=$RUN2/rerank.sock
    warm_svc "$sock" > "$d/warm-$k.txt" 2>&1; rc=$?
    echo "warm-up $k: $(cat "$d/warm-$k.txt") (rc $rc)"
    [ $rc = 0 ] || { echo "$c: the warm-up of $k was not answered"; return 1; }
  done
  sleep "$WARM_SETTLE_S"
  warmed=$(gpu); echo "$warmed" > "$d/gpu-after-warmup.txt"
  echo "$c: GPU after the warm-up (the steady state): $warmed MiB (raw $raw, base $BASE)"
  stop_sampler LOADSAMP
  start_sampler "$d/gpu.txt" SAMP  # the judged window: from after the warm-up to the end of the 10 at once
  for k in one two; do
    if [ $k = one ]; then m=$a; sock=$RUN1/rerank.sock; else m=$b; sock=$RUN2/rerank.sock; fi
    echo "-- the probe's peak on $k ($m), at its bound"
    probe_svc "$sock" "${CHARS[$m]:-24000}" "${BATCH[$m]:-16}" > "$d/probe-$k.txt" 2>&1
    rc=$?; echo "$rc" > "$d/probe-$k.rc"; cat "$d/probe-$k.txt"; echo "probe $k rc $rc; GPU now $(gpu) MiB"
    [ $rc = 0 ] || ok=0
  done
  [ $ok = 1 ] || { echo "$c: a probe shape reached the budget or was not answered: not eligible, its searches not run"; return 2; }
  export GOV_RX_RERANK_DIR=$RUN1 GOV_RX_RERANK_MODEL="${ID[$a]}@${REV[$a]}" GOV_RX_RERANK_DIR2=$RUN2 GOV_RX_RERANK_MODEL2="${ID[$b]}@${REV[$b]}"
  export GOV_RX_LIVE_RULE="$RULE" GOV_RX_GPU_LIMIT_MIB=$BUDGET GOV_RX_LIVE_PARALLEL=${PAR:-0} GOV_RERANK_TIMEOUT_S=30
  export GOV_RX_BATCH=${BATCH[$a]:-16} GOV_RX_REQUEST_CHARS=${CHARS[$a]:-24000} GOV_RX_MODEL_CUT=${MCUT[$a]:-0}
  export GOV_RX_BATCH2=${BATCH[$b]:-16} GOV_RX_REQUEST_CHARS2=${CHARS[$b]:-24000} GOV_RX_MODEL_CUT2=${MCUT[$b]:-0}
  rc=0
  for mode in alone once; do
    [ $mode = alone ] && n=$N_ALONE || n=$N_ONCE
    echo "-- $c: $n searches $([ $mode = alone ] && echo 'one at a time' || echo 'at once')"
    searches $mode $n "$d"; rc=$?
    tail -3 "$d/$mode.txt"
    [ $rc = 0 ] || { echo "$c: the $mode searches ended with $rc"; break; }
  done
  unset GOV_RX_RERANK_DIR GOV_RX_RERANK_MODEL GOV_RX_RERANK_DIR2 GOV_RX_RERANK_MODEL2 GOV_RX_LIVE_RULE GOV_RX_GPU_LIMIT_MIB \
    GOV_RX_LIVE_PARALLEL GOV_RX_BATCH GOV_RX_REQUEST_CHARS GOV_RX_MODEL_CUT GOV_RX_BATCH2 GOV_RX_REQUEST_CHARS2 GOV_RX_MODEL_CUT2
  return $rc
}
run_cell() {  # the judged sampler ends with the 10 at once (or wherever the cell stopped)
  local rc
  run_cell_body "$1"; rc=$?
  stop_sampler SAMP; stop_sampler LOADSAMP
  return $rc
}
end_cell() {  # both services stopped by group, back to the base
  local c=$1 d=$OUT/$1
  mark_to "$c"
  stop_services
  disarm
  [ -s "$d/gpu.txt" ] && echo "$c: judged GPU peak $(sort -n "$d/gpu.txt" | tail -1) MiB; samples at or above $BUDGET: $(awk -v b=$BUDGET '$1 >= b' "$d/gpu.txt" | wc -l) of $(wc -l < "$d/gpu.txt")"
  [ -s "$d/gpu-load.txt" ] && echo "$c: load peak $(sort -n "$d/gpu-load.txt" | tail -1) MiB (reported only)"
  warm
  for i in $(seq 1 $BASE_TRIES); do [ "$(gpu)" -le $((BASE + 300)) ] && break; sleep "$BASE_EVERY"; done
  echo "$c: GPU after the stop $(gpu) MiB (base $BASE)"
  [ "$(gpu)" -le $((BASE + 300)) ] || stop "the GPU did not return to the base after $c"
  CUR=""
}
cleanup() {  # every exit path, once: the samplers, the measure, both services, the backstop, the verdicts, the live service, the hold
  rc=$?; trap - EXIT INT TERM
  stop_sampler SAMP; stop_sampler LOADSAMP
  [ -n "$CUR" ] && mark_to "$CUR"
  stop_services
  disarm
  [ "${DRY:-0}" = 1 ] || verdicts
  [ "$LIVE_STOPPED" = 1 ] && restore
  release_hold
  echo "== $(date '+%F %T') the live window ends (exit $rc)"
  exit $rc
}

if [ "${DRY:-0}" != 1 ]; then OUT=$P/live-window/$(date +%Y%m%d-%H%M%S); mkdir -p "$OUT"; exec > >(tee -a "$OUT/window.log") 2>&1; fi
trap cleanup EXIT; trap 'exit 130' INT; trap 'exit 143' TERM

echo "== $(date '+%F %T') live two-model window: ${CELLS[*]} (DRY=${DRY:-0}, PAR=${PAR:-0})"
MODELS=(); for c in "${CELLS[@]}"; do [ -n "${ONE[$c]:-}" ] || stop "unknown cell $c (M2 or M3)"; MODELS+=("${ONE[$c]}" "${TWO[$c]}"); done
conditions
if [ "${DRY:-0}" = 1 ]; then
  plan
  echo "DRY: $NOTMET condition(s) not met; nothing stopped or started"
  exit 0
fi
embedders
take_hold
stop_live
warm; BASE=$(gpu); echo "base GPU (the live service stopped, both embedders warm): $BASE MiB"
slots_after_stop
MG=$(ps -o pgid= -p $$ | tr -d ' ')
for c in "${CELLS[@]}"; do
  CUR=$c
  run_cell "$c"; echo "$c: measures exit $?"
  end_cell "$c"
done
echo "== all cells measured"
