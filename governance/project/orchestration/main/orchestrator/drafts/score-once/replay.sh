#!/usr/bin/env bash
# SCORE-ONCE replays (D4B-SCORE-ONCE §2-§4): one variant and one combine rule over the window's kept scores, on the
# 138, with no reranker called (GOV_RX_COMBINE). The route answers come from the grid's 0.6B cache (a copy, its scores
# and model mark removed), so every replay asks the same candidate lists. Counts only.
#   replay.sh <name> '<GOV_RX json>' '<rule json>'
# e.g. replay.sh r0 "$V456RQ" '{"kind":"alone","m":"q06"}'
set -uo pipefail
NAME=$1 VARIANT=$2 RULE=$3
S=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/drafts/score-once
CA=$HOME/gov-os-runs/D4B/score-once/caches; RC=$HOME/gov-os-runs/D4B/score-once-replay/caches/$NAME
[ -e "$RC" ] && { echo "replay $NAME exists: $RC"; exit 2; }
mkdir -p "$RC"
python3 - "$CA/q06/cache.db" "$RC/cache.db" <<'EOF' || exit 1
import shutil, sqlite3, sys
shutil.copyfile(sys.argv[1], sys.argv[2])
db = sqlite3.connect(sys.argv[2]); db.execute("DELETE FROM score"); db.execute("DELETE FROM meta"); db.commit()
EOF
MODELS='{"q06":"Qwen/Qwen3-Reranker-0.6B@e61197ed45024b0ed8a2d74b80b4d909f1255473","q4b":"Qwen/Qwen3-Reranker-4B@22e683669bc0f0bd69640a1354a6d0aebcfeede5","gte":"Alibaba-NLP/gte-reranker-modernbert-base@f7481e6055501a30fb19d090657df9ec1f79ab2c","zer":"zeroentropy/zerank-1-small-reranker@a65fd51c450e9b47fdddab98e31166ecad21af8d"}'
CACHES="{\"q06\":\"$CA/q06\",\"q4b\":\"$CA/q4b\",\"gte\":\"$CA/gte\",\"zer\":\"$CA/zer\"}"
export GOV_RX_COMBINE="{\"models\":$MODELS,\"caches\":$CACHES,\"rule\":$RULE}"
unset GOV_RX_RERANK_DIR GOV_RX_RERANK_MODEL
rc=0
for set in r80 r60; do
  bash "$S/so_measure.sh" score-once-replay "$NAME" "$set" "$VARIANT" "$RC" || rc=1
done
P=$HOME/gov-os-runs/D4B/score-once-replay/$NAME
[ $rc = 0 ] && python3 /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/drafts/d4b/score138.py "$NAME" "$P/r80/measure.txt" "$P/r60/measure.txt"
exit $rc
