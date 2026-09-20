#!/bin/bash
# P2-AR-0053: run the R4-O1 probe against this worktree's release `gov`. $1 = output suffix (default: the HEAD short id).
set -u
HERE=$(cd "$(dirname "$0")" && pwd)
WT=$(cd "$HERE/../../../../../.." && pwd)
GOV="$WT/target/release/gov"
SUF=${1:-$(git -C "$WT" rev-parse --short HEAD)}
SCR=$WT/target/P2-AR-0053/r4-o1-scratch-$(date +%s)
mkdir -p "$SCR"
for k in $(env | grep -o '^GOV_[A-Z_]*'); do unset "$k"; done
PROBE="$HERE/tools_install_task_close.py"
{
  echo "# P2-AR-0053 R4-O1 probe run"
  echo "# probe sha256 $(sha256sum "$PROBE" | cut -d' ' -f1)"
  echo "# tree $WT HEAD $(git -C "$WT" rev-parse HEAD) dirty-product-files $(git -C "$WT" status --porcelain -- runtime cli framework tests | wc -l)"
  echo "# gov $GOV sha256 $(sha256sum "$GOV" | cut -d' ' -f1)"
  echo "# date $(date -u +%FT%TZ)"
  GOV_BIN="$GOV" WS07R3_SCRATCH="$SCR" python3 "$PROBE" 2>&1
  echo "[exit=$?]"
} > "$HERE/tools_install_task_close.$SUF.out"
echo "wrote $HERE/tools_install_task_close.$SUF.out"
