#!/usr/bin/env bash
# Build + builder regression suites (AC-15 regression evidence; O3: builder tests are regression, not independent).
# HOME is redirected to a scratch dir so lib tests that open protected machine state cannot touch the real one;
# XDG_STATE_HOME / XDG_CACHE_HOME are UNSET so the defaults ($HOME/.local/state, $HOME/.cache) apply, as on a
# normal workstation. (Contrast 00-regression-variant-xdg-cache.*.)
cd "$(dirname "$0")/../../../../.." || exit 1
S="$(mktemp -d "${PROBE_TMP:-${TMPDIR:-/tmp}}/alpha-r-regress-XXXXXX")"
export CARGO_HOME="${CARGO_HOME:-$HOME/.cargo}" RUSTUP_HOME="${RUSTUP_HOME:-$HOME/.rustup}"
export HOME="$S"; unset XDG_STATE_HOME XDG_CACHE_HOME XDG_CONFIG_HOME
for v in $(env | sed -n 's/^\(GOV_[A-Z_]*\)=.*/\1/p'); do unset "$v"; done
echo "## cargo build --release"; "$CARGO_HOME/bin/cargo" build --release 2>&1 | tail -3
ls -la target/release/gov; sha256sum target/release/gov
echo "## gov version"; target/release/gov --json version
echo "## cargo test --release --lib"; "$CARGO_HOME/bin/cargo" test --release --lib 2>&1 | grep -E '^test result|^running|FAILED|panicked'
echo "## cargo test --release --test certification"; "$CARGO_HOME/bin/cargo" test --release --test certification 2>&1 | grep -E '^test |^test result|^running|FAILED|panicked'
