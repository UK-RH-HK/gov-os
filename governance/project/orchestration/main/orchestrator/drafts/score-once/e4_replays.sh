#!/usr/bin/env bash
# E4 step 3 (E3-E5-DESIGN §1), after e4_window.sh, with no GPU and no reranker: the score-once harness builds today's
# bundle on window 4's clone by M3 (zerank-1-small + gte, merged: min-max over the 40, equal weights) and by M1 (the
# 0.6B + gte, merged), D4B-SCORE-ONCE's rules (grid.txt g-M3, g-M1), as E0b's run B: v456 + rq + L3's lift_norm 0.0766,
# GOV_RX_POOL_OFF=1, strict (any text a model lacks stops the run; GOV_RX_LIVE_MISSING unset). Each cell on a fresh
# copy of E0b's run-B cache (its route answers: E0b's candidate lists; its own scores: run A's 314 0.6B texts, read
# after the kept caches). so_measure.sh keeps every search's output under ~/gov-os-eval/runs/e4/<cell>-<set>/ (mode
# 700); a question's first call is the bundle E4's reader run uses (e3_run.py's first_calls() on the cell's
# measure.txt). Then the figures (e0_figures.py) and each cell against E0b's run B question for question. Counts only.
#   bash e4_replays.sh [m3 m1]      (DRY=1: the conditions and the plan only; nothing written)
# This file has no test seam: test_e4.py runs a temporary copy with one stubs line before the OUT line below.
set -uo pipefail
for v in $(compgen -e); do case "$v" in GOV_RX*|E4_*) unset "$v";; esac; done
R=/home/usain/Dynamic-Agentic-Engineering-OS; O=$R/.gov-runtime/scratch/orchestrator; S=$O/drafts/score-once
D=$O/drafts/d4b; P=$HOME/gov-os-runs/D4B; CLONE=$P/w4-e0/repo; COMMIT=c00d525fd420
E=$P/e0b/caches; Q=$P/e4; QC=$Q/caches; CNT=$Q/count; POINT=e4
VARIANT='{"sem_uncut":true,"sem_k":60,"lex_k":60,"depth":40,"perfile":2,"dedup":true,"rq":"question","lift_norm":0.0766}'
Q06=Qwen/Qwen3-Reranker-0.6B@e61197ed45024b0ed8a2d74b80b4d909f1255473
GTE=Alibaba-NLP/gte-reranker-modernbert-base@f7481e6055501a30fb19d090657df9ec1f79ab2c
ZER=zeroentropy/zerank-1-small-reranker@a65fd51c450e9b47fdddab98e31166ecad21af8d
B80=$P/e0b/b/r80/measure.txt; B60=$P/e0b/b/r60/measure.txt
if [ $# -gt 0 ]; then CELLS=("$@"); else CELLS=(m3 m1); fi
declare -A COMBINE LABEL
COMBINE[m3]="{\"models\":{\"zer\":\"$ZER\",\"gte\":\"$GTE\"},\"caches\":{\"zer\":\"$QC/zer\",\"gte\":\"$QC/gte\"},\"rule\":{\"kind\":\"merge\",\"a\":\"zer\",\"b\":\"gte\"}}"
COMBINE[m1]="{\"models\":{\"q06\":\"$Q06\",\"gte\":\"$GTE\"},\"caches\":{\"q06\":\"$E/seed\",\"gte\":\"$QC/gte\"},\"rule\":{\"kind\":\"merge\",\"a\":\"q06\",\"b\":\"gte\"}}"
LABEL[m3]="E4 M3 (zerank + gte, merged)"; LABEL[m1]="E4 M1 (the 0.6B + gte, merged)"
OUT=""

stop() { echo "STOP: $*"; exit 1; }
NOTMET=0
need() {
  local what=$1; shift
  if "$@"; then echo "ok:      $what"; else echo "NOT MET: $what"; NOTMET=$((NOTMET + 1)); [ "${DRY:-0}" = 1 ] || stop "$what"; fi
}
PINNED=(rx.py so_measure.sh seed_scores.py rerank_worker.py e4_prep.sh e4_prepare.py e4_count.py e4_window.sh e4_replays.sh)
pinned() {  # every file listed in the pin, and each as reviewed
  local f
  for f in "${PINNED[@]}"; do grep -qE "^[0-9a-f]{64}  $f\$" "$S/E4-REVIEWED.sha256" 2>/dev/null || return 1; done
  ( cd "$S" && sha256sum --quiet -c E4-REVIEWED.sha256 )
}
at_commit() { [ "$(git -C "$CLONE" rev-parse --short=12 HEAD 2>/dev/null)" = "$COMMIT" ]; }
quietly() { "$@" > /dev/null 2>&1; }  # a condition whose own line the need line already shows (review F7)
held() { python3 "$S/e4_count.py" --check "$CNT" "$@"; }  # held <name> <cache ...>: 0 lacking
fresh() { local c; for c in "${CELLS[@]}"; do [ -e "$P/$POINT/$c" ] && return 1; done; return 0; }
known() { local c; for c in "${CELLS[@]}"; do [ -n "${COMBINE[$c]:-}" ] || return 1; done; return 0; }
conditions() {
  need "the reviewed E4 files ($S/E4-REVIEWED.sha256)" pinned
  need "the clone at $COMMIT" at_commit
  need "every cell named is m3 or m1" known
  need "no output of these cells yet ($P/$POINT/<cell>)" fresh
  need "E0b's run-B cache, the 0.6B's seed and run B's measures" test -s "$E/b/cache.db" -a -s "$E/seed/cache.db" -a -s "$B80" -a -s "$B60"
  case " ${CELLS[*]} " in *" m3 "*) need "zerank holds every text the replays ask ($(held zer "$QC/zer" 2>&1 | tail -1))" quietly held zer "$QC/zer";; esac
  need "gte holds every text the replays ask ($(held gte "$QC/gte" 2>&1 | tail -1))" quietly held gte "$QC/gte"
  # review F5: the 0.6B checked in what M1's replay reads: E0b's seed, then its own cache, a fresh copy of run B's
  case " ${CELLS[*]} " in *" m1 "*) need "the 0.6B holds every text the replays ask ($(held q06 "$E/seed" "$E/b" 2>&1 | tail -1))" quietly held q06 "$E/seed" "$E/b";; esac
}
plan() {
  local c
  for c in "${CELLS[@]}"; do
    echo "plan $c (${LABEL[$c]}): own cache $QC/own-$c = a fresh copy of $E/b; GOV_RX_COMBINE=${COMBINE[$c]}"
    echo "  so_measure.sh $POINT $c r80, then r60: variant $VARIANT; CLONE=$CLONE GOV_RX_POOL_OFF=1 GOV_RX_GPU_LIMIT_MIB=14255; strict"
    echo "  must read: unscored 0, texts scored live 0; kept outputs ~/gov-os-eval/runs/$POINT/$c-r80/, $c-r60/ (first call per question: the E4 bundle)"
    echo "  figures: e0_figures.py; against E0b's run B: score138.py --same (reported)"
  done
}
replay() {  # replay <cell> <set>
  CLONE=$CLONE GOV_RX_POOL_OFF=1 GOV_RX_GPU_LIMIT_MIB=14255 GOV_RX_COMBINE="${COMBINE[$1]}" \
    bash "$S/so_measure.sh" "$POINT" "$1" "$2" "$VARIANT" "$QC/own-$1"
}
strict_ok() {  # strict_ok <cell> <set>: the summary line of so_measure.sh says nothing was scored and nothing unscored
  local line; line=$(grep "^$1 $2: " "$P/$POINT/measure.log" | tail -1)
  echo "$line"
  case "$line" in *"unscored 0;"*"texts scored live (GOV_RX_LIVE_MISSING) 0;"*) return 0;; *) return 1;; esac
}
copy_own() { rm -rf "$QC/own-$1"; cp -a "$E/b" "$QC/own-$1"; }
figures() { python3 -I "$D/e0_figures.py" "${LABEL[$1]}" "$P/$POINT/$1/r80/measure.txt" "$P/$POINT/$1/r60/measure.txt"; }
against_b() { python3 -I "$D/score138.py" --same "$P/$POINT/$1/r80/measure.txt" "$P/$POINT/$1/r60/measure.txt" "$B80" "$B60"; }

if [ "${DRY:-0}" != 1 ]; then OUT=$Q/replays-$(date +%Y%m%d-%H%M%S).log; mkdir -p "$Q"; exec > >(tee -a "$OUT") 2>&1; fi
echo "== $(date '+%F %T') E4 replays: ${CELLS[*]} (DRY=${DRY:-0})"
conditions
if [ "${DRY:-0}" = 1 ]; then
  plan
  echo "DRY: $NOTMET condition(s) not met; nothing written"
  exit 0
fi
for c in "${CELLS[@]}"; do
  echo "== $(date '+%F %T') $c: ${LABEL[$c]}"
  copy_own "$c"
  for set in r80 r60; do
    replay "$c" "$set" || stop "$c $set: the replay failed (a text lacking stops it, by design; see $P/$POINT/$c/$set/rx.err)"
    strict_ok "$c" "$set" || stop "$c $set: not strict (a text scored or unscored)"
  done
  figures "$c"
  against_b "$c"
done
echo "== $(date '+%F %T') E4 replays done; the bundles: ~/gov-os-eval/runs/$POINT/<cell>-<set>/, first calls by $P/$POINT/<cell>/<set>/measure.txt"
