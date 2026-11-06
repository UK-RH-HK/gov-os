#!/usr/bin/env bash
# DEC-1084's extend window: the 0.6B scores, once, the texts that L5 (phrasing and the term map) and an 80-candidate
# pool ask and the kept q06 cache lacks; each cell is then a replay (replay.sh with REPLAY_ROUTES and REPLAY_Q06 on the
# variant's own cache), judged by D4B-SCORE-ONCE §4's rule against B0. Built on score_once_window.sh's frame: the live
# service stopped for the window and restored (class 3's start line) on EVERY exit path (one trap); the trial service
# started once by setsid, its pid and group checked, READY on cuda; the backstop on this script's, the service's and
# the measure's groups, re-armed per measure, each new one checked alive before the old one stops; the harness stops
# at the budget (14,255 MiB); every stop by pid or group (L-0075); at the end the GPU back to the base. Counts only.
#   setsid bash extend_window.sh [b0 d80 split termmap split-termmap]   (DRY=1: the conditions and the plan only)
# Each variant runs so_measure.sh's r80 and r60 with GOV_RX_RERANK_DIR on the trial socket, into its own copy of the
# kept q06 cache (~/gov-os-runs/D4B/score-once/caches/q06; copied by sqlite's backup, its scores and meta kept), so
# only the missing texts are scored on the GPU. All on v456 with "rq":"question","lift_norm":0.0766 (L3):
#   b0             L3 itself: the path's own check, run first: it must score no new text and give B0's replay
#                  question for question (score138.py --same against g-B0), or the window stops;
#   d80            "depth": 80 (L3's step 0.0766 was set from the 40-candidate passes; kept for it, as declared);
#   split          "split": true;      termmap   "termmap": true;      split-termmap   both.
# Per variant: the texts newly scored (r80, r60, all), the measure's figure (score138.py), the GPU peak and the
# samples at or above the budget, and the replay's command line.
set -uo pipefail
unset GOV_RERANK_GPU_SLOT
for v in $(compgen -e); do case "$v" in GOV_RX*) unset "$v";; esac; done
R=/home/usain/Dynamic-Agentic-Engineering-OS; O=$R/.gov-runtime/scratch/orchestrator; D=$O/drafts/d4b
S=$O/drafts/score-once; P=$HOME/gov-os-runs/D4B; CLONE=$P/g1/repo; KEPT=$P/score-once/caches/q06
POINT=score-once-extend; X=$P/$POINT; XC=$X/caches
V=~/.local/share/gov-os/reranker-trial-venv; TR=~/.local/share/gov-os/rerank-trial
ID=Qwen/Qwen3-Reranker-0.6B; REV=e61197ed45024b0ed8a2d74b80b4d909f1255473; HFH=$HOME/.cache/huggingface; MODEL=$ID@$REV
BUDGET=14255; LIVE_LOG=~/.cache/gov-os/rerank.log
B0_80=$P/score-once-replay/g-B0/r80/measure.txt; B0_60=$P/score-once-replay/g-B0/r60/measure.txt
L3V='{"sem_uncut":true,"sem_k":60,"lex_k":60,"depth":40,"perfile":2,"dedup":true,"rq":"question","lift_norm":0.0766}'
declare -A VAR
VAR[b0]=$L3V
VAR[d80]='{"sem_uncut":true,"sem_k":60,"lex_k":60,"depth":80,"perfile":2,"dedup":true,"rq":"question","lift_norm":0.0766}'
VAR[split]='{"sem_uncut":true,"sem_k":60,"lex_k":60,"depth":40,"perfile":2,"dedup":true,"rq":"question","lift_norm":0.0766,"split":true}'
VAR[termmap]='{"sem_uncut":true,"sem_k":60,"lex_k":60,"depth":40,"perfile":2,"dedup":true,"rq":"question","lift_norm":0.0766,"termmap":true}'
VAR[split-termmap]='{"sem_uncut":true,"sem_k":60,"lex_k":60,"depth":40,"perfile":2,"dedup":true,"rq":"question","lift_norm":0.0766,"split":true,"termmap":true}'
if [ $# -gt 0 ]; then VARIANTS=("$@"); else VARIANTS=(b0 d80 split termmap split-termmap); fi
if [ "${DRY:-0}" != 1 ]; then mkdir -p "$X"; exec > >(tee -a "$X/window.log") 2>&1; fi

gpu() { nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits | head -1; }
warm() {  # page both embedders in, so a base or a return-to-base reading is not low by Windows' paging
  curl -s -m 60 http://127.0.0.1:11434/api/embed -d '{"model":"qwen3-embedding:0.6b","input":"warm"}' > /dev/null
  curl -s -m 60 http://127.0.0.1:11435/api/embed -d '{"model":"qwen3-embedding:0.6b","input":"warm"}' > /dev/null
  sleep 5
}
LIVE_STOPPED=0; SVC=""; SP=""; BS=""; SAMP=""; HELD=0; MP=""; MG=""
restore() {
  ( cd /home/usain/gov-os-worktrees/W2-00-store && GOV_RERANK_IDLE_S=43200 ~/.local/bin/gov retrieve "what decides a close" --json > /dev/null 2>&1 )
  by=$(cd /home/usain/gov-os-worktrees/W2-00-store && ~/.local/bin/gov retrieve "what decides a close" --json 2>/dev/null | python3 -c "import json,sys; print((json.load(sys.stdin)['result'].get('rerank') or {}).get('by'))")
  echo "restore: $(tail -1 $LIVE_LOG); class 3's check: rerank.by = $by; GPU $(gpu) MiB"
  printf '{"at": "%s", "class": 3, "reason": "the extend window ended (DEC-1084)", "check": "rerank.by %s"}\n' "$(date '+%F %T')" "$by" >> $O/log/restarts.jsonl
}
alive_pid() { kill -0 "$1" 2>/dev/null && [ "$(ps -o stat= -p "$1" 2>/dev/null | cut -c1)" != Z ]; }
disarm() { [ -n "$BS" ] && bash $O/tools/proc.sh stop --grace 5 "$BS" > /dev/null 2>&1; BS=""; }
arm() {  # the backstop on the groups given; the new one checked alive after a second before the old one stops
  local old=$BS
  setsid bash $O/tools/gpu_backstop.sh "$@" < /dev/null > /dev/null 2>&1 & BS=$!
  sleep 1
  if ! alive_pid "$BS"; then BS=$old; stop "the backstop on groups $* did not stay up: the run is not left unguarded"; fi
  [ -n "$old" ] && bash $O/tools/proc.sh stop --grace 5 "$old" > /dev/null 2>&1
  echo "backstop pid $BS on groups $*"
}
cleanup() {  # every exit path, once: the sampler, the measure, the trial service, the backstop, the live service, the hold
  rc=$?; trap - EXIT INT TERM
  [ -n "$SAMP" ] && kill "$SAMP" 2>/dev/null
  [ -n "$MP" ] && { echo "cleanup: stopping the measure's group $MP"; bash $O/tools/proc.sh stop --grace 10 "-$MP"; }
  [ -n "$SVC" ] && { echo "cleanup: stopping the trial service group ${SVC#-}"; bash $O/tools/proc.sh stop --grace 30 "$SVC"; }
  disarm
  [ "$LIVE_STOPPED" = 1 ] && restore
  [ "$HELD" = 1 ] && [ -e $O/log/act-in-progress.txt ] && mv $O/log/act-in-progress.txt $O/log/act-in-progress.ended-$(date +%H%M)-extend.txt
  echo "== $(date '+%F %T') the extend window ends (exit $rc)"
  exit $rc
}
trap cleanup EXIT; trap 'exit 130' INT; trap 'exit 143' TERM
stop() { echo "STOP: $*"; exit 1; }
NOTMET=0
need() {  # need "<condition>" <command ...>: DRY lists every condition; a real run stops at the first not met
  local what=$1; shift
  if "$@"; then echo "ok:      $what"; else echo "NOT MET: $what"; NOTMET=$((NOTMET + 1)); [ "${DRY:-0}" = 1 ] || stop "$what"; fi
}
kept_ok() { python3 - "$KEPT/cache.db" "$MODEL" <<'EOF'
import sqlite3, sys
db = sqlite3.connect(f"file:{sys.argv[1]}?mode=ro", uri=True)
meta = dict(db.execute("SELECT k, v FROM meta").fetchall())
n, m = db.execute("SELECT COUNT(*) FROM score").fetchone()[0], db.execute("SELECT COUNT(*) FROM memo").fetchone()[0]
print(f"         the kept q06 cache: {n} scores, {m} route answers, model {meta.get('rerank_model')}")
sys.exit(0 if meta.get("rerank_model") == sys.argv[2] and "rerank_model2" not in meta and n > 0 else 1)
EOF
}
count() { python3 -c "import sqlite3, sys; print(sqlite3.connect(f'file:{sys.argv[1]}?mode=ro', uri=True).execute('SELECT COUNT(*) FROM score').fetchone()[0])" "$1"; }
lock_free() { [ ! -e "$1" ] || flock -n "$1" true; }
quiet() { grep -q "heavy slots held: none" $O/dispatch/status.txt && grep -q "^Jobs by phase: none" $O/dispatch/status.txt; }
no_act() { [ ! -e $O/log/act-in-progress.txt ]; }
phrasings_on() { grep -qE '^\s*phrasings:\s*true' "$CLONE/governance/project/retrieval.yaml"; }
fresh() { local v; for v in "${VARIANTS[@]}"; do [ -e "$XC/$v" ] || [ -e "$X/$v" ] && return 1; done; return 0; }
known() { local v; for v in "${VARIANTS[@]}"; do [ -n "${VAR[$v]:-}" ] || return 1; done; return 0; }
control_first() { [ "${NO_CONTROL:-0}" = 1 ] || [ "${VARIANTS[0]}" = b0 ]; }
slots_free() { local i n=0; for i in 0 1; do lock_free /tmp/gov-os-rerank-gpu-$i.lock && n=$((n + 1)); done; echo $n; }

echo "== $(date '+%F %T') extend window: ${VARIANTS[*]} (DRY=${DRY:-0})"
need "the reviewed extend files ($S/EXTEND-REVIEWED.sha256: rx.py, extend_window.sh, so_measure.sh, replay.sh, rerank_worker.py)" \
  sha256sum --quiet -c "$S/EXTEND-REVIEWED.sha256"
need "the trial service's worker is the reviewed score-once copy" cmp -s $S/rerank_worker.py $TR/svc/rerank_worker.py
need "the trial service and its venv" test -f "$TR/svc/rerank_service.py" -a -x "$V/bin/python"
need "the 0.6B's snapshot $ID@${REV:0:8} under $HFH" test -d "$HFH/hub/models--${ID//\//--}/snapshots/$REV"
need "every variant named is known (b0 d80 split termmap split-termmap)" known
need "the kept q06 cache, the 0.6B's alone ($KEPT)" kept_ok
need "the control b0 runs first (NO_CONTROL=1 to drop it)" control_first
need "B0's replay measures (the control's reference: g-B0 r80 and r60)" test -s "$B0_80" -a -s "$B0_60"
need "each variant scores once: no cache or output of it yet under $X" fresh
need "routing.phrasings on at the measure clone (L5 extends it; off, the harness refuses)" phrasings_on
need "quiet (the dispatcher: no heavy slot held, no job)" quiet
need "no ACT in progress" no_act
need "the trial lock free ($TR/run/rerank.lock)" lock_free "$TR/run/rerank.lock"
need "the scorer, the measure and the stop and backstop tools" test -f $D/score138.py -a -f $S/so_measure.sh -a -f $O/tools/proc.sh -a -f $O/tools/gpu_backstop.sh
[ -e "$TR/run/rerank.sock" ] && echo "note:    a socket at $TR/run/rerank.sock with its lock free is stale; it is removed before the start"
dirty=$(git -C "$CLONE" status --porcelain --untracked-files=no | wc -l)
echo "the measure clone at $(git -C "$CLONE" rev-parse --short=12 HEAD), $dirty tracked file(s) changed (0: the term map is kept in each cache; else rebuilt in each process, the same map); GPU now $(gpu) MiB"
if [ "${DRY:-0}" = 1 ]; then
  echo "plan: the live service stopped; the base read with both embedders warm; one trial service, $MODEL (HF_HOME=$HFH, the cross-encoder, 16 texts and 24,000 characters a request, GOV_RERANK_TRIAL_RELEASE=1), on $TR/run"
  for v in "${VARIANTS[@]}"; do
    echo "plan $v: copy $KEPT -> $XC/$v (scores and meta kept); so_measure.sh $POINT $v r80, then r60, variant ${VAR[$v]}; GOV_RX_RERANK_DIR=$TR/run GOV_RX_GPU_LIMIT_MIB=$BUDGET; then texts newly scored, score138, GPU peak$([ $v = b0 ] && echo '; must score 0 new texts and equal g-B0 question for question, or the window stops')$([ $v = d80 ] && echo '; L3 step 0.0766 kept as declared (set from the 40-candidate passes)')"
  done
  echo "plan: the replay of each: REPLAY_ROUTES=$XC/<v> REPLAY_Q06=$XC/<v> bash $S/replay.sh ext-<v> '<its variant>' '{\"kind\":\"alone\",\"m\":\"q06\"}' (it must give the window's figure, as R0 did)"
  echo "DRY: $NOTMET condition(s) not met; nothing stopped or started"
  exit 0
fi
need "the shared embedder answers (:11434)" curl -s -m 10 -o /dev/null http://127.0.0.1:11434/api/version
need "the query embedder answers (:11435)" curl -s -m 10 -o /dev/null http://127.0.0.1:11435/api/version
printf 'EXTEND (DEC-1084): the CTO'"'"'s own hold for the extend window, from %s\n' "$(date '+%F %T')" > $O/log/act-in-progress.txt; HELD=1
LP=$(grep READY $LIVE_LOG | tail -1 | grep -oE 'pid [0-9]+' | awk '{print $2}')
LIVE_STOPPED=1
if [ -n "$LP" ] && tr '\0' ' ' < /proc/$LP/cmdline 2>/dev/null | grep -q 'gov/retrieval/rerank_service.py'; then
  bash $O/tools/proc.sh stop --grace 30 "$LP" || stop "the live service did not stop"
fi
warm; BASE=$(gpu); echo "base GPU (the live service stopped, both embedders warm): $BASE MiB"
[ "$(slots_free)" -ge 1 ] || stop "no GPU reranker slot free (slots 0-1) for the trial service"
MG=$(ps -o pgid= -p $$ | tr -d ' ')

# the trial service, once
[ -e "$TR/run/rerank.sock" ] && rm -f "$TR/run/rerank.sock"
n=$(wc -l < $TR/run/rerank.log); t0=$(date +%s.%N)
( exec 9>"$TR/run/rerank.lock"; flock -n 9 || exit 1
  HF_HOME=$HFH HF_HUB_OFFLINE=1 GOV_RERANK_IDLE_S=3600 GOV_RERANK_TRIAL_8BIT=0 GOV_RERANK_TRIAL_LOADER= GOV_RERANK_TRIAL_RELEASE=1 \
    setsid "$V/bin/python" -I "$TR/svc/rerank_service.py" "$ID" "$REV" "$TR/run/rerank.sock" 9 >> "$TR/run/service.log" 2>&1 < /dev/null &
  echo $! > "$X/svc.pid" ) || stop "the trial service did not start (the trial lock is held)"
SP=$(cat "$X/svc.pid"); SVC="-$SP"  # its own group from the start: a slow load is stopped by it, never orphaned
arm "$MG" "$SP"
for i in $(seq 1 300); do tail -n +$((n+1)) $TR/run/rerank.log | grep -qE 'READY|REFUSED|END' && break; sleep 1; done
ST=$(tail -n +$((n+1)) $TR/run/rerank.log | grep -E 'READY|REFUSED|END' | head -1)
echo "load: $(echo "$(date +%s.%N) - $t0" | bc) s; $ST; service group $SP; GPU $(gpu) MiB (base $BASE)"
case "$ST" in *READY*cuda*) ;; *) tail -5 $TR/run/service.log; stop "the 0.6B did not load on the GPU within 300 s";; esac
[ "$(bash $O/tools/proc.sh pgid "$SP")" = "$SP" ] || stop "the trial service's process group is not its own pid $SP"
case "$ST" in *"pid $SP "*) ;; *) stop "the READY line names another pid than the service's $SP: $ST";; esac
export GOV_RX_RERANK_DIR=$TR/run GOV_RX_RERANK_MODEL=$MODEL GOV_RX_GPU_LIMIT_MIB=$BUDGET CLONE=$CLONE

for v in "${VARIANTS[@]}"; do
  echo "== $(date '+%F %T') $v: ${VAR[$v]}"
  mkdir -p "$XC/$v"
  python3 - "$KEPT/cache.db" "$XC/$v/cache.db" <<'EOF' || stop "the cache copy failed"
import sqlite3, sys
src = sqlite3.connect(f"file:{sys.argv[1]}?mode=ro", uri=True)
dst = sqlite3.connect(sys.argv[2])
src.backup(dst)  # scores, route answers and meta kept: only the texts the kept cache lacks are scored
print(f"cache: {dst.execute('SELECT COUNT(*) FROM score').fetchone()[0]} scores and "
      f"{dst.execute('SELECT COUNT(*) FROM memo').fetchone()[0]} route answers copied")
EOF
  c0=$(count "$XC/$v/cache.db")
  nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits -lms 1000 > "$X/gpu-$v.txt" & SAMP=$!
  rc=0; declare -A AT=()
  for set in r80 r60; do
    setsid bash $S/so_measure.sh "$POINT" "$v" "$set" "${VAR[$v]}" "$XC/$v" & MP=$!
    arm "$MG" "$SP" "$MP"
    wait $MP || rc=1
    MP=""
    AT[$set]=$(count "$XC/$v/cache.db")
    [ $rc = 0 ] || break
  done
  arm "$MG" "$SP"
  kill $SAMP 2>/dev/null; SAMP=""
  c1=${AT[r80]:-$c0}; c2=${AT[r60]:-$c1}
  echo "$v: texts newly scored: r80 $((c1 - c0)), r60 $((c2 - c1)), all $((c2 - c0)) (cache $c0 -> $c2); GPU peak $(sort -n "$X/gpu-$v.txt" | tail -1) MiB; samples at or above $BUDGET: $(awk -v b=$BUDGET '$1 >= b' "$X/gpu-$v.txt" | wc -l)"
  [ $rc = 0 ] || stop "$v's runs failed (see $X/measure.log)"
  python3 $D/score138.py "$v" "$X/$v/r80/measure.txt" "$X/$v/r60/measure.txt"
  if [ "$v" = b0 ]; then  # the path's own check: L3 again scores nothing new and gives B0's replay
    [ $((c2 - c0)) = 0 ] || stop "the control scored $((c2 - c0)) new texts: the window's path does not ask the grid's texts"
    python3 $D/score138.py --same "$X/b0/r80/measure.txt" "$X/b0/r60/measure.txt" "$B0_80" "$B0_60" \
      || stop "the control does not give B0's replay question for question: the path is not faithful"
  fi
  echo "replay: REPLAY_ROUTES=$XC/$v REPLAY_Q06=$XC/$v bash $S/replay.sh ext-$v '${VAR[$v]}' '{\"kind\":\"alone\",\"m\":\"q06\"}'"
done
unset GOV_RX_RERANK_DIR GOV_RX_RERANK_MODEL GOV_RX_GPU_LIMIT_MIB
echo "-- the stop, by the service's group"
bash $O/tools/proc.sh stop --grace 30 "$SVC"; SVC=""
disarm
warm
for i in $(seq 1 60); do [ "$(gpu)" -le $((BASE + 300)) ] && break; sleep 5; done
echo "GPU after the stop $(gpu) MiB (base $BASE)"
[ "$(gpu)" -le $((BASE + 300)) ] || stop "the GPU did not return to the base"
echo "== all variants scored once"
