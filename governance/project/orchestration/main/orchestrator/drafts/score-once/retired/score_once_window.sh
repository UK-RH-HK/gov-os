#!/usr/bin/env bash
# SCORE-ONCE's one quiet GPU window (DEC-1081 (3), D4B-SCORE-ONCE §1): the four rerankers each score every kept
# candidate list of the 138 once (v456: 40 reranked per question), each into a kept cache of its own, on the same
# candidate lists (the 0.6B's route answers copied to the others' caches, its scores not). One reranker on the GPU at
# a time, on the trial copy's own socket, with the live service stopped for the window and restored after it (class
# 3's start line) on EVERY exit path (one trap). The GPU rules: the backstop on this script's and the service's
# process groups; the harness stops at the budget (14,255 MiB); between models the GPU back to the base (read with
# both embedders warm); every stop and wait by pid and bounded (L-0075). Counts only.
#   setsid bash score_once_window.sh [q06f q06 q4b gte zer]   (DRY=1: the checks and the plan only; nothing starts)
set -uo pipefail
R=/home/usain/Dynamic-Agentic-Engineering-OS; O=$R/.gov-runtime/scratch/orchestrator; D=$O/drafts/d4b
S=$O/drafts/score-once; P=$HOME/gov-os-runs/D4B; SO=$P/score-once; CA=$SO/caches
V=~/.local/share/gov-os/reranker-trial-venv; TR=~/.local/share/gov-os/rerank-trial; C=~/.cache/gov-os-trial
V456='{"sem_uncut":true,"sem_k":60,"lex_k":60,"depth":40,"perfile":2,"dedup":true}'
# D4B-SCORE-ONCE v2: the grid's runs give the depth rerank the question (the product's form, L5's finding a5c0c34f);
# q06f runs v456 as every past figure was measured, for the trial path's faithfulness check only
V456RQ='{"sem_uncut":true,"sem_k":60,"lex_k":60,"depth":40,"perfile":2,"dedup":true,"rq":"question"}'
LIVE_LOG=~/.cache/gov-os/rerank.log
KEPT80=$P/trial-w4-t2-qwen06b/r80/run1/measure.txt; KEPT60=$P/trial-w4-t2-qwen06b/r60/run1/measure.txt
if [ $# -gt 0 ]; then MODELS=("$@"); else MODELS=(q06f q06 q4b gte zer); fi
declare -A ID REV HFH BIT LOADER BATCH CHARS MCUT VAR
ID[q06f]=Qwen/Qwen3-Reranker-0.6B;                REV[q06f]=e61197ed45024b0ed8a2d74b80b4d909f1255473; HFH[q06f]=$HOME/.cache/huggingface; VAR[q06f]=$V456
ID[q06]=Qwen/Qwen3-Reranker-0.6B;                 REV[q06]=e61197ed45024b0ed8a2d74b80b4d909f1255473; HFH[q06]=$HOME/.cache/huggingface
ID[q4b]=Qwen/Qwen3-Reranker-4B;                   REV[q4b]=22e683669bc0f0bd69640a1354a6d0aebcfeede5; HFH[q4b]=$C/hf; BIT[q4b]=1; BATCH[q4b]=8; CHARS[q4b]=12000
ID[gte]=Alibaba-NLP/gte-reranker-modernbert-base; REV[gte]=f7481e6055501a30fb19d090657df9ec1f79ab2c; HFH[gte]=$C/hf
ID[zer]=zeroentropy/zerank-1-small-reranker;      REV[zer]=a65fd51c450e9b47fdddab98e31166ecad21af8d; HFH[zer]=$C/hf; LOADER[zer]=yes-logit; MCUT[zer]=10000
mkdir -p "$SO" "$CA"
exec > >(tee -a "$SO/window.log") 2>&1
gpu() { nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits | head -1; }
warm() {  # page both embedders in, so a base or a return-to-base reading is not low by Windows' paging
  curl -s -m 60 http://127.0.0.1:11434/api/embed -d '{"model":"qwen3-embedding:0.6b","input":"warm"}' > /dev/null
  curl -s -m 60 http://127.0.0.1:11435/api/embed -d '{"model":"qwen3-embedding:0.6b","input":"warm"}' > /dev/null
  sleep 5
}
LIVE_STOPPED=0; SVC=""; BS=""; SAMP=""; HELD=0; MP=""
restore() {
  ( cd /home/usain/gov-os-worktrees/W2-00-store && GOV_RERANK_IDLE_S=43200 ~/.local/bin/gov retrieve "what decides a close" --json > /dev/null 2>&1 )
  by=$(cd /home/usain/gov-os-worktrees/W2-00-store && ~/.local/bin/gov retrieve "what decides a close" --json 2>/dev/null | python3 -c "import json,sys; print((json.load(sys.stdin)['result'].get('rerank') or {}).get('by'))")
  echo "restore: $(tail -1 $LIVE_LOG); class 3's check: rerank.by = $by; GPU $(gpu) MiB"
  printf '{"at": "%s", "class": 3, "reason": "the score-once window ended (DEC-1081 (3))", "check": "rerank.by %s"}\n' "$(date '+%F %T')" "$by" >> $O/log/restarts.jsonl
}
cleanup() {  # every exit path, once: the trial service by its pid, the sampler, the backstop, the live service, the hold
  rc=$?; trap - EXIT INT TERM
  [ -n "$SAMP" ] && kill "$SAMP" 2>/dev/null
  [ -n "$MP" ] && { echo "cleanup: stopping the measure's group $MP"; bash $O/tools/proc.sh stop --grace 10 "-$MP"; }
  [ -n "$SVC" ] && { echo "cleanup: stopping the trial service group $SVC"; bash $O/tools/proc.sh stop --grace 30 "$SVC"; }
  [ -n "$BS" ] && bash $O/tools/proc.sh stop --grace 5 "$BS" > /dev/null 2>&1
  [ "$LIVE_STOPPED" = 1 ] && restore
  [ "$HELD" = 1 ] && [ -e $O/log/act-in-progress.txt ] && mv $O/log/act-in-progress.txt $O/log/act-in-progress.ended-$(date +%H%M)-score-once.txt
  echo "== $(date '+%F %T') the window ends (exit $rc)"
  exit $rc
}
trap cleanup EXIT; trap 'exit 130' INT; trap 'exit 143' TERM
stop() { echo "STOP: $*"; exit 1; }

echo "== $(date '+%F %T') score-once window: ${MODELS[*]} (DRY=${DRY:-0})"
# the conditions (nothing is stopped or started before they all hold)
sha256sum --quiet -c "$S/REVIEWED.sha256" || stop "a score-once file differs from its reviewed form (REVIEWED.sha256)"
cmp -s $S/rerank_worker.py $TR/svc/rerank_worker.py || stop "the trial service's worker is not the reviewed score-once copy"
diff -rq $R/fixtures/evaluation/memory-retrieval/visible $HOME/gov-os-eval/fixtures/evaluation/memory-retrieval/visible > /dev/null || stop "the sets root's visible half is not integrate's"
grep -q "heavy slots held: none" $O/dispatch/status.txt && grep -q "^Jobs by phase: none" $O/dispatch/status.txt || stop "not quiet (the dispatcher)"
[ -e $O/log/act-in-progress.txt ] && stop "an ACT is in progress: $(cat $O/log/act-in-progress.txt)"
flock -n "$TR/run/rerank.lock" true || stop "a trial service holds the trial lock"
[ -s "$KEPT80" ] && [ -s "$KEPT60" ] || stop "the kept 0.6B run (the faithfulness check's reference) is missing"
for m in "${MODELS[@]}"; do [ -n "${ID[$m]:-}" ] || stop "unknown model $m"; done
for m in "${MODELS[@]}"; do [ -e "$CA/$m/cache.db" ] && stop "$CA/$m exists: a model scores once"; done
[ "${MODELS[0]}" = q06f ] || { [ -s "$CA/q06f/cache.db" ] && { [ "${MODELS[0]}" = q06 ] || [ -s "$CA/q06/cache.db" ]; }; } \
  || stop "q06f runs first, then q06 (their route answers are the others' candidate lists)"
echo "conditions ok; GPU now $(gpu) MiB"
if [ "${DRY:-0}" = 1 ]; then
  for m in "${MODELS[@]}"; do echo "plan: $m = ${ID[$m]}@${REV[$m]} HF_HOME=${HFH[$m]} 8bit=${BIT[$m]:-0} loader=${LOADER[$m]:-cross-encoder} batch=${BATCH[$m]:-16} chars=${CHARS[$m]:-24000} model-cut=${MCUT[$m]:-0} cache=$CA/$m variant=${VAR[$m]:-$V456RQ}"; done
  exit 0
fi
printf 'SCORE-ONCE (DEC-1081 (3)): the CTO'"'"'s own hold for the score-once window, from %s\n' "$(date '+%F %T')" > $O/log/act-in-progress.txt; HELD=1
LP=$(grep READY $LIVE_LOG | tail -1 | grep -oE 'pid [0-9]+' | awk '{print $2}')
if [ -n "$LP" ] && tr '\0' ' ' < /proc/$LP/cmdline 2>/dev/null | grep -q 'gov/retrieval/rerank_service.py'; then
  LIVE_STOPPED=1
  bash $O/tools/proc.sh stop --grace 30 "$LP" || stop "the live service did not stop"
fi
LIVE_STOPPED=1
warm; BASE=$(gpu); echo "base GPU (the live service stopped, both embedders warm): $BASE MiB"
MG=$(ps -o pgid= -p $$ | tr -d ' ')

for m in "${MODELS[@]}"; do
  echo "== $(date '+%F %T') $m: ${ID[$m]}@${REV[$m]}"
  mkdir -p "$CA/$m"
  SRC=""; [ "$m" = q06 ] && SRC=q06f; [ "$m" != q06f ] && [ "$m" != q06 ] && SRC=q06
  if [ -n "$SRC" ]; then  # the same candidate lists: the 0.6B's route answers, none of its scores, no model mark
    python3 - "$CA/$SRC/cache.db" "$CA/$m/cache.db" <<'EOF' || stop "the cache copy failed"
import shutil, sqlite3, sys
shutil.copyfile(sys.argv[1], sys.argv[2])
db = sqlite3.connect(sys.argv[2]); db.execute("DELETE FROM score"); db.execute("DELETE FROM meta"); db.commit()
print(f"cache: {db.execute('SELECT COUNT(*) FROM memo').fetchone()[0]} route answers copied, "
      f"{db.execute('SELECT COUNT(*) FROM score').fetchone()[0]} scores")
EOF
  fi
  n=$(wc -l < $TR/run/rerank.log); t0=$(date +%s.%N)
  ( exec 9>"$TR/run/rerank.lock"; flock -n 9 || exit 1
    HF_HOME=${HFH[$m]} HF_HUB_OFFLINE=1 GOV_RERANK_IDLE_S=3600 GOV_RERANK_TRIAL_8BIT=${BIT[$m]:-0} \
      GOV_RERANK_TRIAL_LOADER=${LOADER[$m]:-} GOV_RERANK_TRIAL_RELEASE=1 \
      setsid "$V/bin/python" -I "$TR/svc/rerank_service.py" "${ID[$m]}" "${REV[$m]}" "$TR/run/rerank.sock" 9 >> "$TR/run/service.log" 2>&1 < /dev/null &
    echo $! > "$SO/svc.pid" ) || stop "the trial service did not start (the trial lock is held)"
  SP=$(cat "$SO/svc.pid"); SVC="-$SP"  # its own process group (setsid), known from the start: a slow load is
  # stopped by this group, never orphaned, whichever process of the group logs READY
  for i in $(seq 1 300); do tail -n +$((n+1)) $TR/run/rerank.log | grep -qE 'READY|REFUSED|END' && break; sleep 1; done
  ST=$(tail -n +$((n+1)) $TR/run/rerank.log | grep -E 'READY|REFUSED|END' | head -1)
  echo "load: $(echo "$(date +%s.%N) - $t0" | bc) s; $ST; service group $SP; GPU $(gpu) MiB (base $BASE)"
  case "$ST" in *READY*cuda*) ;; *) tail -5 $TR/run/service.log; stop "$m did not load on the GPU within 300 s";; esac
  [ "$(bash $O/tools/proc.sh pgid "$SP")" = "$SP" ] || stop "the trial service's process group is not its own pid $SP"
  case "$ST" in *"pid $SP "*) ;; *) stop "the READY line names another pid than the service's $SP: $ST";; esac
  nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits -lms 1000 > "$SO/gpu-$m.txt" & SAMP=$!
  export GOV_RX_RERANK_DIR=$TR/run GOV_RX_RERANK_MODEL="${ID[$m]}@${REV[$m]}" GOV_RX_GPU_LIMIT_MIB=14255 CLONE=$P/g1/repo
  export GOV_RX_BATCH=${BATCH[$m]:-16} GOV_RX_REQUEST_CHARS=${CHARS[$m]:-24000} GOV_RX_MODEL_CUT=${MCUT[$m]:-0}
  rc=0  # each measure in its own process group, waited on in the background, so a signal runs the trap at once
  for set in r80 r60; do
    setsid bash $S/so_measure.sh score-once "$m" "$set" "${VAR[$m]:-$V456RQ}" "$CA/$m" & MP=$!
    # the backstop on all three groups (this script's, the service's, the measure's), armed per measure
    setsid bash $O/tools/gpu_backstop.sh "$MG" "$SP" "$MP" < /dev/null > /dev/null 2>&1 & BS=$!
    wait $MP || rc=1
    MP=""
    bash $O/tools/proc.sh stop --grace 5 "$BS" > /dev/null 2>&1; BS=""
    [ $rc = 0 ] || break
  done
  unset GOV_RX_RERANK_DIR GOV_RX_RERANK_MODEL GOV_RX_BATCH GOV_RX_REQUEST_CHARS GOV_RX_MODEL_CUT
  kill $SAMP 2>/dev/null; SAMP=""
  echo "$m: GPU peak during its runs $(sort -n "$SO/gpu-$m.txt" | tail -1) MiB; samples over 14,255: $(awk '$1 >= 14255' "$SO/gpu-$m.txt" | wc -l)"
  bash $O/tools/proc.sh stop --grace 30 "$SVC"; SVC=""
  [ $rc = 0 ] || stop "$m's runs failed (see $SO/measure.log)"
  warm
  for i in $(seq 1 60); do [ "$(gpu)" -le $((BASE + 300)) ] && break; sleep 5; done
  echo "$m: GPU after the stop $(gpu) MiB (base $BASE)"
  [ "$(gpu)" -le $((BASE + 300)) ] || stop "the GPU did not return to the base after $m"
  # the same candidate lists as the grid's 0.6B (q06, the same rerank text), checked before the next model (not first
  # at replay): no new route answer, and the 0.6B's number of scored texts
  if [ "$m" != q06f ] && [ "$m" != q06 ]; then
    python3 - "$CA/q06/cache.db" "$CA/$m/cache.db" "$m" <<'EOF' || stop "$m did not score the 0.6B's candidate lists"
import sqlite3, sys
a, b = (sqlite3.connect(f"file:{p}?mode=ro", uri=True) for p in sys.argv[1:3])
count = lambda db, t: db.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
memo_a, memo_b, sa, sb = count(a, "memo"), count(b, "memo"), count(a, "score"), count(b, "score")
print(f"{sys.argv[3]}: route answers {memo_b} (the 0.6B's {memo_a}); scored texts {sb} (the 0.6B's {sa})")
sys.exit(0 if (memo_a == memo_b and sa == sb) else 1)
EOF
  fi
  python3 $D/score138.py "$m" "$SO/$m/r80/measure.txt" "$SO/$m/r60/measure.txt"
  if [ "$m" = q06f ]; then  # the trial path's own check: the 0.6B as its kept run (trial-w4-t2-qwen06b, 107 of 138)
    python3 $D/score138.py --same "$SO/q06f/r80/measure.txt" "$SO/q06f/r60/measure.txt" "$KEPT80" "$KEPT60" \
      || stop "the 0.6B does not reproduce its kept run: the path is not faithful"
  fi
done
echo "== all models scored once"
