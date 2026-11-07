#!/usr/bin/env bash
# E4 step 1 (E3-E5-DESIGN §1; E0B-RESULT "Next"), before any window: no GPU, no reranker, nothing stopped or started.
#  1. the seeds: gte's and zerank's kept scores (score-once/caches/gte, zer; seed_scores.py: scores only, no route
#     answer, each source one model);
#  2. the window caches: each seed plus E0b's route answers on window 4's clone (e4_prepare.py routes: E0b run A's
#     cache, its store checked against the clone's now), so the window's trial runs ask the routes nothing new and score
#     only the texts the seed lacks;
#  3. the count: a strict replay of E0b's run B (the 0.6B alone, v456 + rq + lift_norm 0.0766, GOV_RX_POOL_OFF=1, on a
#     fresh copy of E0b's run-B cache) whose gov is e4_count.py: every pass's texts keyed for q06, gte and zer and looked
#     up in their caches (q06: E0b's seed + run A's own cache; gte, zer: their seeds), digests only;
#  4. the counts (distinct texts asked, lacking, per model) and the replay against E0b's run B question for question
#     (it must equal it: the count replay is run B again).
# Counts only. Outputs: ~/gov-os-runs/D4B/e4/{caches,count,prep.log}. Run it once; it refuses an existing count.
#   bash e4_prep.sh            (DRY=1: the conditions and the plan only; nothing written)
set -uo pipefail
for v in $(compgen -e); do case "$v" in GOV_RX*|E4_*) unset "$v";; esac; done
R=/home/usain/Dynamic-Agentic-Engineering-OS; O=$R/.gov-runtime/scratch/orchestrator; D=$O/drafts/d4b
S=$O/drafts/score-once; P=$HOME/gov-os-runs/D4B; CLONE=$P/w4-e0/repo; E=$P/e0b/caches; K=$P/score-once/caches
Q=$P/e4; QC=$Q/caches; CNT=$Q/count; TMP=/tmp/gov-os-emg-e4; COMMIT=c00d525fd420
Q06=Qwen/Qwen3-Reranker-0.6B@e61197ed45024b0ed8a2d74b80b4d909f1255473
GTE=Alibaba-NLP/gte-reranker-modernbert-base@f7481e6055501a30fb19d090657df9ec1f79ab2c
ZER=zeroentropy/zerank-1-small-reranker@a65fd51c450e9b47fdddab98e31166ecad21af8d
VL3='{"sem_uncut":true,"sem_k":60,"lex_k":60,"depth":40,"perfile":2,"dedup":true,"rq":"question","lift_norm":0.0766}'
B80=$P/e0b/b/r80/measure.txt; B60=$P/e0b/b/r60/measure.txt

stop() { echo "STOP: $*"; exit 1; }
NOTMET=0
need() {
  local what=$1; shift
  if "$@"; then echo "ok:      $what"; else echo "NOT MET: $what"; NOTMET=$((NOTMET + 1)); [ "${DRY:-0}" = 1 ] || stop "$what"; fi
}
pinned() { ( cd "$S" && sha256sum --quiet -c E0B-REVIEWED.sha256 ); }
at_commit() { [ "$(git -C "$CLONE" rev-parse --short=12 HEAD 2>/dev/null)" = "$COMMIT" ]; }
routes_fresh() {  # E0b's caches hold the clone's store now (a rebuild since would change its head)
  local want; want=$(python3 "$S/e4_prepare.py" store "$CLONE") || return 1
  python3 -c "import sqlite3, sys; sys.exit(0 if all(sqlite3.connect(f'file:{p}/cache.db?mode=ro', uri=True).execute(\"SELECT v FROM meta WHERE k = 'store'\").fetchone() == (sys.argv[1],) for p in sys.argv[2:]) else 1)" "$want" "$E/a" "$E/b"
}
fresh_count() { [ ! -e "$CNT" ]; }
quiet() { grep -q "heavy slots held: none" $O/dispatch/status.txt && grep -q "^Jobs by phase: none" $O/dispatch/status.txt; }

echo "== $(date '+%F %T') E4 prep (DRY=${DRY:-0})"
need "the E0b harness files as reviewed (E0B-REVIEWED.sha256: rx.py, so_measure.sh, seed_scores.py)" pinned
need "the clone $CLONE at $COMMIT" at_commit
need "E0b's caches ($E/seed, a, b) and run B's measures (the count's reference)" test -s "$E/seed/cache.db" -a -s "$E/a/cache.db" -a -s "$E/b/cache.db" -a -s "$B80" -a -s "$B60"
need "E0b's route answers are the clone's store's now (no rebuild since)" routes_fresh
need "the kept gte and zerank caches ($K/gte, $K/zer)" test -s "$K/gte/cache.db" -a -s "$K/zer/cache.db"
need "no count yet ($CNT)" fresh_count
need "quiet (the dispatcher: no heavy slot held, no job)" quiet
if [ "${DRY:-0}" = 1 ]; then
  echo "plan: seeds $QC/gte-seed <- $K/gte; $QC/zer-seed <- $K/zer (seed_scores.py; each made once, kept if present)"
  echo "plan: window caches $QC/gte, $QC/zer = seed + E0b run A's route answers ($E/a), store checked (e4_prepare.py routes)"
  echo "plan: the count: strict replay, gov e4_count.py, rule q06 alone (caches q06 $E/seed + own $CNT/own = copy of $E/b), variant $VL3, GOV_RX_POOL_OFF=1; counted: q06 in $E/seed + $E/a, gte in $QC/gte-seed, zer in $QC/zer-seed; r80 then r60 through heavy_slot.sh"
  echo "plan: then e4_count.py --summary $CNT, and score138.py --same against E0b run B ($B80, $B60): 0 differing"
  echo "DRY: $NOTMET condition(s) not met; nothing written"
  exit 0
fi
mkdir -p "$Q" "$QC" "$TMP"
exec > >(tee -a "$Q/prep.log") 2>&1
for m in gte zer; do
  [ -e "$QC/$m-seed/cache.db" ] || python3 "$S/seed_scores.py" "$QC/$m-seed" "$K/$m" || stop "the $m seed"
  [ -e "$QC/$m/cache.db" ] || python3 "$S/e4_prepare.py" routes "$QC/$m" "$QC/$m-seed" "$E/a" "$CLONE" || stop "the $m window cache"
done
mkdir -p "$CNT"; cp -a "$E/b" "$CNT/own"
export E4_COUNT="{\"q06\":{\"model\":\"$Q06\",\"caches\":[\"$E/seed\",\"$E/a\"]},\"gte\":{\"model\":\"$GTE\",\"caches\":[\"$QC/gte-seed\"]},\"zer\":{\"model\":\"$ZER\",\"caches\":[\"$QC/zer-seed\"]}}"
export E4_COUNT_DIR=$CNT GOV_RX_POOL_OFF=1 GOV_RX_GPU_LIMIT_MIB=14255
export GOV_RX_COMBINE="{\"models\":{\"q06\":\"$Q06\"},\"caches\":{\"q06\":\"$E/seed\"},\"rule\":{\"kind\":\"alone\",\"m\":\"q06\"}}"
for set in r80 r60; do
  case "$set" in r80) MSET=memory-retrieval PART=all ;; r60) MSET=memory-verdict PART=hidden ;; esac
  d=$CNT/$set; mkdir -p "$d"; : > "$d/rx.log"
  W=$TMP/gov-count-$set
  printf '%s\n' '#!/usr/bin/env bash' \
    "case \"\$1\" in --version) PYTHONPATH=\"$CLONE/src\" exec python3 $S/rx.py \"\$@\" ;; esac" \
    "GOV_RX='$VL3' GOV_RX_CACHE=\"$CNT/own\" GOV_RX_LOG=\"$d/rx.log\" PYTHONPATH=\"$CLONE/src\" exec python3 $S/e4_count.py \"\$@\" 2>> \"$d/rx.err\"" > "$W"
  chmod +x "$W"
  t0=$(date +%s)
  echo "== $(date '+%F %T') the count, $set, on $(git -C "$CLONE" rev-parse --short=12 HEAD)"
  env -u GOV_TICKET GOV_ROLE=orchestrator TMPDIR=$TMP PYTHONPATH="$CLONE/src" bash "$O/tools/heavy_slot.sh" \
    python3 -m gov.retrieval.measure "$MSET" --root "$CLONE" --sets-root "$HOME/gov-os-eval" --part "$PART" \
    --out "$d" --gov "$W" > "$d/measure.txt" 2> "$d/measure.err" || stop "the count's measure $set failed (see $d/measure.err, $d/rx.err)"
  echo "$set: $(( $(date +%s) - t0 )) s; combined passes $(grep -c '^combine' "$d/rx.log"); texts read from the replay's own cache $(awk -F'\t' '$1 == "OWNCACHE" {n += $2} END {print n + 0}' "$d/rx.log"); unscored $(grep -c '^UNSCORED' "$d/rx.log")"
done
unset E4_COUNT E4_COUNT_DIR GOV_RX_POOL_OFF GOV_RX_GPU_LIMIT_MIB GOV_RX_COMBINE
echo "== the counts (distinct texts, digests only)"
python3 "$S/e4_count.py" --summary "$CNT"
echo "== the count replay against E0b's run B (must be 0 differing)"
python3 -I "$D/score138.py" --same "$CNT/r80/measure.txt" "$CNT/r60/measure.txt" "$B80" "$B60"
python3 -I "$D/e0_figures.py" "the count replay (E0b B again)" "$CNT/r80/measure.txt" "$CNT/r60/measure.txt"
echo "== $(date '+%F %T') E4 prep done"
