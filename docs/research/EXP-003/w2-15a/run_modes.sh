#!/usr/bin/env bash
# W2-15a: W2-61's measure on D-4b's m1 clone, once per mode (modes.py), one after another, each after any running
# rebuild has ended (the D-4b rebuild lock). Only the CTO's session runs it (the hidden half: ids and counts only).
#   bash run_modes.sh <mode>...      (lexical semantic fused rerank)
set -euo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
R=/home/usain/Dynamic-Agentic-Engineering-OS
CLONE=$HOME/gov-os-runs/D4B/m1/repo
RUN=$HOME/gov-os-runs/W2-15a
RAW=$HERE/raw
mkdir -p "$RUN" "$RAW"
for MODE in "$@"; do
  cat > "$RUN/gov-$MODE" <<EOF
#!/usr/bin/env bash
GOV_W215A_LOG="$RAW/rerank-$MODE.log" PYTHONPATH="$CLONE/src" exec python3 "$HERE/modes.py" $MODE "\$@"
EOF
  chmod +x "$RUN/gov-$MODE"
  flock /tmp/gov-os-d4b-rebuild.lock true  # wait out a rebuild in progress
  t0=$(date +%s)
  env -u GOV_TICKET GOV_ROLE=orchestrator TMPDIR=/tmp/gov-os-emg-w215a PYTHONPATH="$CLONE/src" \
    bash "$R/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh" python3 -m gov.retrieval.measure memory-retrieval \
    --root "$CLONE" --sets-root "$HOME/gov-os-eval" --part all --out "$RAW/records-$MODE" --gov "$RUN/gov-$MODE" \
    > "$RAW/measure-$MODE.txt" 2> "$RAW/measure-$MODE.err" || echo "MEASURE FAILED ($MODE)"
  echo "$MODE: $(( $(date +%s) - t0 )) s; $(tail -1 "$RAW/measure-$MODE.txt")"
done
