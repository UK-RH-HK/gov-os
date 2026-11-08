#!/usr/bin/env bash
# E4 on the fresh 80, steps 1 and 2 (data only, not judged; DEC-1097 (1)(c), (5)): after the hold ends.
#   setsid bash f80_e4_prep.sh --sets-root ~/gov-os-eval > ~/gov-os-runs/fresh-80/e4-prep.out 2>&1 < /dev/null &
# From drafts/d4b/e0b_run.sh (the 80's candidate lists and the 0.6B's scores through the score-once harness) and
# drafts/score-once/e4_prep.sh (the seeds, the window caches, the count), on the set memory-verdict-2, part hidden:
#  A. run A: the 0.6B alone, v456 + rq, no lift, GOV_RX_LIVE_MISSING=1 (the texts no kept cache holds scored on the
#     LIVE 0.6B service: the one light GPU job, the backstop armed on this group), GOV_RX_POOL_OFF=1, E0's clone; the
#     q06 seed is E0b's (read only); its own cache new. It fills the route answers (the 80's candidate lists).
#  B. run B: L3's lift_norm 0.0766, strict, on a fresh copy of A's cache (no GPU): the 0.6B in B0's form.
#  C. the seeds: gte's and zerank's scores from the kept caches and E4's window caches (seed_scores.py, scores only);
#     the window caches: each seed plus run A's route answers (e4_prepare.py routes, the store checked).
#  D. the count: a strict replay of run B whose gov is e4_count.py (q06 in E0b's seed and A's cache; gte, zer in their
#     seeds); then e4_count.py --summary: the texts each model lacks, which f80_e4_window.sh scores.
# Every folder under <root>/runs/fresh-80/data/e4/ (derived here; refused if it exists). rx.py, seed_scores.py,
# e4_prepare.py and e4_count.py are used as reviewed (E4-REVIEWED.sha256, E0B-REVIEWED.sha256); the fresh-80 files as
# pinned (FRESH80-REVIEWED.sha256). Standard output: counts only, the paths of the run folder named "<run folder>".
#   DRY=1: the conditions and the plan only; nothing written.
set -uo pipefail
for v in $(compgen -e); do case "$v" in GOV_RX*|E4_*) unset "$v";; esac; done
R=/home/usain/Dynamic-Agentic-Engineering-OS; O=$R/.gov-runtime/scratch/orchestrator; S=$O/drafts/score-once
F=$O/drafts/fresh80; P=$HOME/gov-os-runs/D4B; CLONE=$P/w4-e0/repo; COMMIT=c00d525fd420
E=$P/e0b/caches; K=$P/score-once/caches; Q4=$P/e4/caches; TMP=/tmp/gov-os-emg-f80e4
Q06=Qwen/Qwen3-Reranker-0.6B@e61197ed45024b0ed8a2d74b80b4d909f1255473
GTE=Alibaba-NLP/gte-reranker-modernbert-base@f7481e6055501a30fb19d090657df9ec1f79ab2c
ZER=zeroentropy/zerank-1-small-reranker@a65fd51c450e9b47fdddab98e31166ecad21af8d
V='{"sem_uncut":true,"sem_k":60,"lex_k":60,"depth":40,"perfile":2,"dedup":true,"rq":"question"}'
VL3='{"sem_uncut":true,"sem_k":60,"lex_k":60,"depth":40,"perfile":2,"dedup":true,"rq":"question","lift_norm":0.0766}'
SETS_ROOT=""
while [ $# -gt 0 ]; do case "$1" in --sets-root) SETS_ROOT=${2:-}; shift 2 || exit 2;; --sets-root=*) SETS_ROOT=${1#*=}; shift;; *) echo "REFUSED: --sets-root <root> only"; exit 2;; esac; done
ROOT=$(realpath -e "$SETS_ROOT" 2>/dev/null) || { echo "REFUSED: --sets-root <root> is required"; exit 2; }
RUNS=$ROOT/runs/fresh-80; Q=$RUNS/data/e4; QC=$Q/caches; CNT=$Q/count
red() { sed -u "s#$RUNS#<run folder>#g; s#$ROOT#<sets root>#g"; }

stop() { echo "STOP: $*"; exit 1; }
NOTMET=0
need() {
  local what=$1; shift
  if "$@"; then echo "ok:      $what"; else echo "NOT MET: $what"; NOTMET=$((NOTMET + 1)); [ "${DRY:-0}" = 1 ] || stop "$what"; fi
}
pinned() { ( cd "$S" && sha256sum --quiet -c E4-REVIEWED.sha256 && sha256sum --quiet -c E0B-REVIEWED.sha256 ) > /dev/null 2>&1 \
  && [ -s "$F/FRESH80-REVIEWED.sha256" ] && ( cd "$F" && sha256sum --quiet -c FRESH80-REVIEWED.sha256 ) > /dev/null 2>&1; }
at_commit() { [ "$(git -C "$CLONE" rev-parse --short=12 HEAD 2>/dev/null)" = "$COMMIT" ]; }
no_hold() { ! grep -q "FRESH-80 HOLD" "$O/log/act-in-progress.txt" 2>/dev/null; }
judged_done() { [ -s "$RUNS/reader/summary.json" ] && python3 -c "import json,sys; d=json.load(open(sys.argv[1])); sys.exit(0 if d.get('rows') == d.get('questions_planned') and not d.get('stopped') else 1)" "$RUNS/reader/summary.json" 2>/dev/null; }  # review R4
act() { "$HOME/.local/share/gov-os/pin-bcea09060ebc/bin/python" "$F/f80_check.py" act --sets-root "$ROOT" > /dev/null 2>&1; }
fresh() { [ ! -e "$Q" ]; }
own_group() { [ "$(ps -o pgid= -p $$ | tr -d ' ')" = "$$" ]; }
quiet() { grep -q "heavy slots held: none" $O/dispatch/status.txt && grep -q "^Jobs by phase: none" $O/dispatch/status.txt; }

echo "== $(date '+%F %T') E4 on the fresh 80, prep (data only, not judged; DRY=${DRY:-0})"
need "GOV_STORE unset (reviewer 1 S6)" test -z "${GOV_STORE+x}"
need "its own process group (setsid)" own_group
need "the reviewed harness files and the pinned fresh-80 files" pinned
need "the clone at $COMMIT" at_commit
need "the hold has ended (data conditions run after it, FRESH-80-1 §3.2 step 10)" no_hold
need "ACT-GUARD-SETS-1 applied (readiness-7 F1)" act
need "the judged reader run finished (every question, no brake stop)" judged_done
need "no E4 output on the 80 yet" fresh
need "E0b's q06 seed, the kept gte and zerank caches, E4's window caches" test -s "$E/seed/cache.db" -a -s "$K/gte/cache.db" -a -s "$K/zer/cache.db" -a -s "$Q4/gte/cache.db" -a -s "$Q4/zer/cache.db"
need "quiet (the dispatcher: no heavy slot held, no job)" quiet
if [ "${DRY:-0}" = 1 ]; then
  echo "plan A: f80_so_measure.sh base a (variant v456 + rq), GOV_RX_LIVE_MISSING=1 GOV_RX_POOL_OFF=1, COMBINE q06 alone (seed: E0b's), own cache <run folder>/data/e4/caches/a; the backstop on this group"
  echo "plan B: f80_so_measure.sh base b (lift_norm 0.0766), strict, own cache a fresh copy of a"
  echo "plan C: seeds gte-seed <- kept gte + E4's window gte; zer-seed <- kept zer + E4's window zer; window caches = seed + a's route answers"
  echo "plan D: the count: strict replay of B with e4_count.py as gov; then e4_count.py --summary"
  echo "DRY: $NOTMET condition(s) not met; nothing written"
  exit 0
fi
unset GOV_STORE GOV_TICKET
mkdir -p "$QC" "$CNT" "$TMP"
exec > >(tee -a "$Q/prep.log" | red) 2>&1
G=$(ps -o pgid= -p $$ | tr -d ' '); setsid bash $O/tools/gpu_backstop.sh "$G" < /dev/null > /dev/null 2>&1 & BS=$!
trap 'bash $O/tools/proc.sh stop --grace 5 "$BS" > /dev/null 2>&1' EXIT
echo "backstop $BS on group $G"
export CLONE GOV_RX_POOL_OFF=1 GOV_RX_GPU_LIMIT_MIB=14255
export GOV_RX_COMBINE="{\"models\":{\"q06\":\"$Q06\"},\"caches\":{\"q06\":\"$E/seed\"},\"rule\":{\"kind\":\"alone\",\"m\":\"q06\"}}"
line() { grep "^$1 v80: " "$Q/$2/measure.log" | tail -1; }
echo "== A (no lift; live-missing on: the live 0.6B scores what no kept cache holds)"
GOV_RX_LIVE_MISSING=1 bash "$F/f80_so_measure.sh" "$ROOT" base a "$V" "$QC/a" || stop "run A"
line a base
echo "== B (lift_norm 0.0766; strict)"
cp -a "$QC/a" "$QC/b"
bash "$F/f80_so_measure.sh" "$ROOT" base b "$VL3" "$QC/b" || stop "run B"
line b base
case "$(line b base)" in *"unscored 0;"*"texts scored live (GOV_RX_LIVE_MISSING) 0;"*) ;; *) stop "run B not strict";; esac
unset GOV_RX_COMBINE
echo "== C: the seeds and the window caches"
python3 "$S/seed_scores.py" "$QC/gte-seed" "$K/gte" "$Q4/gte" || stop "the gte seed"
python3 "$S/seed_scores.py" "$QC/zer-seed" "$K/zer" "$Q4/zer" || stop "the zer seed"
python3 "$S/e4_prepare.py" routes "$QC/gte" "$QC/gte-seed" "$QC/a" "$CLONE" || stop "the gte window cache"
python3 "$S/e4_prepare.py" routes "$QC/zer" "$QC/zer-seed" "$QC/a" "$CLONE" || stop "the zer window cache"
echo "== D: the count (a strict replay of B; e4_count.py as gov; no reranker)"
cp -a "$QC/b" "$CNT/own"
export E4_COUNT="{\"q06\":{\"model\":\"$Q06\",\"caches\":[\"$E/seed\",\"$QC/a\"]},\"gte\":{\"model\":\"$GTE\",\"caches\":[\"$QC/gte-seed\"]},\"zer\":{\"model\":\"$ZER\",\"caches\":[\"$QC/zer-seed\"]}}"
export E4_COUNT_DIR=$CNT
export GOV_RX_COMBINE="{\"models\":{\"q06\":\"$Q06\"},\"caches\":{\"q06\":\"$E/seed\"},\"rule\":{\"kind\":\"alone\",\"m\":\"q06\"}}"
d=$CNT/v80; mkdir -p "$d"; : > "$d/rx.log"
W=$TMP/gov-count-v80
printf '%s\n' '#!/usr/bin/env bash' \
  "case \"\$1\" in --version) PYTHONPATH=\"$CLONE/src\" exec python3 $S/rx.py \"\$@\" ;; esac" \
  "GOV_RX='$VL3' GOV_RX_CACHE=\"$CNT/own\" GOV_RX_LOG=\"$d/rx.log\" PYTHONPATH=\"$CLONE/src\" exec python3 $S/e4_count.py \"\$@\" 2>> \"$d/rx.err\"" > "$W"
chmod 700 "$W"
env -u GOV_TICKET -u GOV_STORE GOV_ROLE=orchestrator TMPDIR=$TMP PYTHONPATH="$CLONE/src" bash "$O/tools/heavy_slot.sh" \
  python3 -m gov.retrieval.measure memory-verdict-2 --root "$CLONE" --sets-root "$ROOT" --part hidden \
  --out "$d" --gov "$W" > "$d/measure.txt" 2> "$d/measure.err" || stop "the count's measure failed"
echo "count: combined passes $(grep -c '^combine' "$d/rx.log"); unscored $(grep -c '^UNSCORED' "$d/rx.log")"
unset E4_COUNT E4_COUNT_DIR GOV_RX_COMBINE GOV_RX_POOL_OFF GOV_RX_GPU_LIMIT_MIB
python3 "$S/e4_count.py" --summary "$CNT"
echo "== $(date '+%F %T') E4 prep on the 80 done; next: DRY=1 then setsid bash f80_e4_window.sh --sets-root ~/gov-os-eval"
