#!/bin/bash
# Rebuild without embeddings, measure the secrets-indexing check on this repository's real store
# (DEC-595) on a quiet machine, then gov close DAEO-7nne on the round's merge.
cd /home/usain/Dynamic-Agentic-Engineering-OS || exit 1
L=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/log
PYTHONPATH=src python3 -m gov.cli.main rebuild --no-embeddings --json > $L/rebuild-W1-15H.json 2> $L/rebuild-W1-15H.err
echo "rebuild exit $?"
echo "load before measurement: $(cut -d' ' -f1-3 /proc/loadavg); processors $(nproc)"
du -sm .gov-runtime | cut -f1
find .gov-runtime -type f | wc -l
S=$(date +%s.%N)
PYTHONPATH=src /usr/bin/time -v python3 -m gov.secrets > $L/secrets-real-store.out 2> $L/secrets-real-store.time
echo "gov.secrets exit $? in $(echo "$(date +%s.%N) - $S" | bc) s; output lines $(wc -l < $L/secrets-real-store.out)"
grep -E "Maximum resident|Elapsed" $L/secrets-real-store.time
PYTHONPATH=src python3 -m gov.cli.main close DAEO-7nne --json --role orchestrator > $L/close-W1-15H.json 2> $L/close-W1-15H.err
echo "close exit $?"
cut -d' ' -f1-3 /proc/loadavg
