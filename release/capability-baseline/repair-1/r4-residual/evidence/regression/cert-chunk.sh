#!/bin/bash
# P2-AR-0043: run a chunk of the certification suite (module filters) in the foreground, output to $OUT.
# usage: cert-chunk.sh <out-file> <threads> <module> [module...]
set -u
WT=/tmp/claude-1000/-home-usain-Dynamic-Agentic-Engineering-OS/1b6c780e-2b37-439f-a969-a8d96b7ad35e/scratchpad/wt/p2-repair1-r4-residual
OUT=$1; shift; TH=$1; shift
export PATH="$HOME/.cargo/bin:$PATH" CARGO_BUILD_JOBS=2
for k in $(env | grep -o '^GOV_[A-Z_]*'); do unset "$k"; done
cd "$WT"
F=()
for m in "$@"; do F+=("$m::"); done
{ echo "# chunk: $*  HEAD $(git rev-parse HEAD)  dirty=$(git status --porcelain -- runtime cli framework tests | wc -l)  $(date -u +%FT%TZ)";
  timeout 590 cargo test --test certification -- --test-threads "$TH" "${F[@]}" 2>&1; echo "[exit=$?]"; } > "$OUT"
grep -E "^test result|^\[exit" "$OUT"; grep -E "^test .*FAILED|^test .* has been running" "$OUT" | grep FAILED
