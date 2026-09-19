#!/usr/bin/env bash
# P2-AR-0034: run one chunk of the certification suite (exact test names), so each invocation fits the tool timeout.
# Usage: cert-chunk.sh <worktree> <list-file> <start> <count> <out-file> [threads]
set -u
WT="$1"; LIST="$2"; START="$3"; COUNT="$4"; OUT="$5"; TH="${6:-6}"
export PATH="$HOME/.cargo/bin:$PATH" CARGO_BUILD_JOBS=2
cd "$WT" || exit 2
mapfile -t NAMES < <(sed -n "$((START+1)),$((START+COUNT))p" "$LIST")
{ echo "# chunk start=$START count=${#NAMES[@]} HEAD=$(git rev-parse HEAD) $(date -u +%FT%TZ)"; printf '#  %s\n' "${NAMES[@]}"; } > "$OUT"
timeout 580 cargo test --test certification -- --exact --test-threads "$TH" "${NAMES[@]}" >> "$OUT" 2>&1
echo "# exit=$?" >> "$OUT"
grep -E "^test result|^test .*FAILED|^# exit" "$OUT"
