#!/usr/bin/env bash
# Re-pin window 4's measures of the two builds (DEC-1074 (5)), one GPU job, run in its own process group (setsid):
#   w4-i   integrate's head, the control: the harness's v456;
#   w4-92  W2-92's build (the stated links): the harness's v456; its drift count (S10);
#   w4-32  W2-32's build: the harness's v456 with the pool off, and the product's own path with S11's pool on.
# Counts only. The GPU backstop is armed on this job's group (never a text match).
set -uo pipefail
O=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator; D=$O/drafts/d4b
OUT=$HOME/gov-os-runs/D4B/w4; mkdir -p "$OUT"; exec > >(tee -a "$OUT/measures.log") 2>&1
G=$(ps -o pgid= -p $$ | tr -d ' '); setsid bash $O/tools/gpu_backstop.sh "$G" < /dev/null > /dev/null 2>&1 & BS=$!
echo "== $(date '+%F %T') window 4's measures; group $G, backstop $BS; GPU $(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits) MiB"
V456='{"sem_uncut":true,"sem_k":60,"lex_k":60,"depth":40,"perfile":2,"dedup":true}'
bash $D/w4_point.sh w4-i  "$1" 0 v456 "$V456"
bash $D/w4_point.sh w4-92 "$2" 0 v456 "$V456"
echo "-- W2-92's drift (S10), on its rebuilt store"
C=$HOME/gov-os-runs/D4B/w4-92/repo
PYTHONPATH=$C/src python3 $C/docs/research/W2-92-proto-drift.py $C $OUT/drift-w4-92.json 2>&1 | tail -14
bash $D/w4_point.sh w4-32 "$3" 1 product '{}' v456-harness "$V456"
echo "-- S11's check: the product with the pool on against the harness's v456, question for question"
P=$HOME/gov-os-runs/D4B/w4-32-rx
python3 $D/score138.py --same $P/product/run1/measure.txt $P/product-60/run1/measure.txt $P/v456-harness/run1/measure.txt $P/v456-harness-60/run1/measure.txt
echo "-- W2-92 against the control (DEC-1071's rule: the 79 not lower, the halves' gap not wider; with the 59 beside)"
python3 $D/score79.py $HOME/gov-os-runs/D4B/w4-i-rx/v456/run1/measure.txt $HOME/gov-os-runs/D4B/w4-92-rx/v456/run1/measure.txt
for p in w4-i w4-92; do python3 $D/score138.py $p $HOME/gov-os-runs/D4B/$p-rx/v456/run1/measure.txt $HOME/gov-os-runs/D4B/$p-rx/v456-60/run1/measure.txt; done
bash $O/tools/proc.sh stop --grace 5 "$BS" > /dev/null 2>&1
echo "== $(date '+%F %T') done; GPU $(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits) MiB"
