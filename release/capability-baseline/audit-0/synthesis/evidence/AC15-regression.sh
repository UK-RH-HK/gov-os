#!/usr/bin/env bash
# P2-AR-0007 AC-15: builder regression on the candidate, exactly the two commands the frozen contract names
# (`cargo test --lib`, `cargo test --test certification`; default profile). Builder tests are regression evidence (O3).
# HOME is redirected to a fresh scratch dir; XDG_* and GOV_* unset (default workstation layout inside the scratch HOME).
# usage: PROBE_TMP=<scratch> bash AC15-regression.sh > AC15-regression.out 2>&1
cd "$(dirname "$0")/../../../../.." || exit 1
S="$(mktemp -d "${PROBE_TMP:-/tmp}/synth-ac15-XXXXXX")"
export CARGO_HOME="${CARGO_HOME:-$HOME/.cargo}" RUSTUP_HOME="${RUSTUP_HOME:-$HOME/.rustup}"
export HOME="$S"; unset XDG_STATE_HOME XDG_CACHE_HOME XDG_CONFIG_HOME
for v in $(env | sed -n 's/^\(GOV_[A-Z_]*\)=.*/\1/p'); do unset "$v"; done
echo "## HEAD $(git rev-parse HEAD)"
python3 release/orchestration/phase-2/tools/product_identity.py HEAD
echo "## \$ cargo test --lib"
"$CARGO_HOME/bin/cargo" test --lib 2>&1 | grep -E '^test |^test result|^running|FAILED|panicked|error'
echo "## \$ cargo test --test certification"
"$CARGO_HOME/bin/cargo" test --test certification 2>&1 | grep -E '^test |^test result|^running|FAILED|panicked|error'
echo "## done $(date -u +%FT%TZ)"
