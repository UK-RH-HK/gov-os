#!/usr/bin/env bash
# Re-runs one replay call by hand, keeping its stderr: the continuation of a kept call, for a VISIBLE question only.
#   repro_call.sh <replay name> <visible question id> <kept call number to continue from> '<GOV_RX json>'
set -uo pipefail
NAME=$1 QID=$2 PREV=$3 VARIANT=$4
CLONE=$HOME/gov-os-runs/D4B/g1/repo; H=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/drafts/score-once
CA=$HOME/gov-os-runs/D4B/score-once/caches
Q=$(python3 -c "import yaml,sys; print(yaml.safe_load(open('$CLONE/fixtures/evaluation/memory-retrieval/visible/$QID.yaml'))['question'])")
TOKEN=$(python3 -c "import json; print(json.load(open('$HOME/gov-os-eval/runs/score-once-replay/$NAME-r80/$(printf %05d $PREV).json'))['result']['continuation'])")
MODELS='{"q06":"Qwen/Qwen3-Reranker-0.6B@e61197ed45024b0ed8a2d74b80b4d909f1255473","q4b":"Qwen/Qwen3-Reranker-4B@22e683669bc0f0bd69640a1354a6d0aebcfeede5","gte":"Alibaba-NLP/gte-reranker-modernbert-base@f7481e6055501a30fb19d090657df9ec1f79ab2c","zer":"zeroentropy/zerank-1-small-reranker@a65fd51c450e9b47fdddab98e31166ecad21af8d"}'
CACHES="{\"q06\":\"$CA/q06\",\"q4b\":\"$CA/q4b\",\"gte\":\"$CA/gte\",\"zer\":\"$CA/zer\"}"
cd "$CLONE"
GOV_RX="$VARIANT" GOV_RX_CACHE=$HOME/gov-os-runs/D4B/score-once-replay/caches/$NAME \
  GOV_RX_COMBINE="{\"models\":$MODELS,\"caches\":$CACHES,\"rule\":{\"kind\":\"alone\",\"m\":\"q06\"}}" \
  PYTHONPATH="$CLONE/src" python3 "$H/rx.py" retrieve --batch-size 10 --bundle-budget 6000 --continue "$TOKEN" "$Q" --json > /tmp/gov-os-emg-so/repro.json
echo "exit $?"
python3 -c "import json; d=json.load(open('/tmp/gov-os-emg-so/repro.json')); print({k: v for k, v in d.items() if k != 'result'})"
