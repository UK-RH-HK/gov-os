#!/bin/bash
# P2-AR-0043: run WS-7's IP probe unedited and its labelled derived copy against this worktree's release gov.
set -u
HERE=$(cd "$(dirname "$0")" && pwd)
WT=$(cd "$HERE/../../../../../.." && pwd)
GOV="$WT/target/release/gov"
SCR=$WT/target/P2-AR-0043/int3-o1-scratch-$(date +%s)
mkdir -p "$SCR"
for k in $(env | grep -o '^GOV_[A-Z_]*'); do unset "$k"; done
hdr() { echo "# P2-AR-0043 INT3-O1 probe run: $1"; echo "# probe sha256 $(sha256sum "$1" | cut -d' ' -f1)";
        echo "# tree $WT HEAD $(git -C "$WT" rev-parse HEAD) dirty-product-files $(git -C "$WT" status --porcelain -- runtime cli framework | wc -l)";
        echo "# gov $GOV sha256 $(sha256sum "$GOV" | cut -d' ' -f1)"; echo "# date $(date -u +%FT%TZ)"; }
ORIG="$WT/release/capability-baseline/repair-1/r3-ws07/evidence/ip_task_close_registration.py"
{ hdr "$ORIG"; GOV_BIN="$GOV" WS07R3_SCRATCH="$SCR/unedited" python3 "$ORIG" 2>&1; echo "[exit=$?]"; } > "$HERE/ip_task_close_registration.unedited.out"
DER="$HERE/ip_task_close_registration.INT3-O1.P2-AR-0043.py"
{ hdr "$DER"; GOV_BIN="$GOV" WS07R3_SCRATCH="$SCR/derived" python3 "$DER" 2>&1; echo "[exit=$?]"; } > "$HERE/ip_task_close_registration.INT3-O1.P2-AR-0043.out"
