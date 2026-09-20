#!/bin/bash
# P2-AR-0054 (round-4 integration): run a chunk of the certification suite (module filters) in the foreground,
# output to $OUT. A copy of P2-AR-0055's `evidence/regression-0055/cert-chunk.P2-AR-0055.sh`; the only changes are
# the worktree path and the chunking (ws01r4 joins repair3's chunk; r4_residual keeps its own).
# usage: cert-chunk.P2-AR-0054.sh <out-file> <threads> <module> [module...]
set -u
WT=/tmp/claude-1000/-home-usain-Dynamic-Agentic-Engineering-OS/1b6c780e-2b37-439f-a969-a8d96b7ad35e/scratchpad/wt/p2-repair1-r4-integration
OUT=$1; shift; TH=$1; shift
export PATH="$HOME/.cargo/bin:$PATH" CARGO_BUILD_JOBS=2
for k in $(env | grep -o '^GOV_[A-Z_]*'); do unset "$k"; done
cd "$WT"
F=()
for m in "$@"; do F+=("$m::"); done
{ echo "# chunk: $*  HEAD $(git rev-parse HEAD)  dirty=$(git status --porcelain -- runtime cli framework tests | wc -l)  $(date -u +%FT%TZ)";
  timeout 590 cargo test --test certification -- --test-threads "$TH" "${F[@]}" 2>&1; echo "[exit=$?]"; } > "$OUT"
grep -E "^test result|^\[exit" "$OUT"; grep -E "^test .*FAILED" "$OUT"
