#!/usr/bin/env bash
# P2-AR-0020 (WS-8) — builder regression (O3: regression evidence only, never acceptance).
#   default  : HOME redirected to scratch, XDG_* unset (a normal workstation layout), GOV_* stripped
#   xdgcache : HOME redirected, XDG_STATE_HOME/XDG_CACHE_HOME set to paths WITHOUT a ".cache" segment
#              (the alpha-r 00-regression-variant-xdg-cache condition behind A0-A2-03)
# Usage: regression.sh <label>   (writes regression-<label>.out beside this script)
set -u
LABEL="${1:?label}"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WT="$(cd "$HERE/../../../../.." && pwd)"
OUT="$HERE/regression-$LABEL.out"
export CARGO_BUILD_JOBS=2
export CARGO_HOME="${CARGO_HOME:-$HOME/.cargo}" RUSTUP_HOME="${RUSTUP_HOME:-$HOME/.rustup}"
CARGO="$CARGO_HOME/bin/cargo"
SCR="${P2AR0020_SCRATCH:?set P2AR0020_SCRATCH}"
for v in $(env | sed -n 's/^\(GOV_[A-Z_]*\)=.*/\1/p'); do unset "$v"; done
cd "$WT" || exit 1
{
  echo "# P2-AR-0020 regression, label=$LABEL"
  echo "# HEAD $(git rev-parse HEAD)  dirty-files: $(git status --porcelain | wc -l)  date $(date -u +%FT%TZ)"
  for mode in default xdgcache; do
    S="$(mktemp -d "$SCR/regress-$mode-XXXXXX")"
    if [ "$mode" = default ]; then
      echo "## mode=default (HOME=$S, XDG_* unset)"
      ENVV=(env -u XDG_STATE_HOME -u XDG_CACHE_HOME -u XDG_CONFIG_HOME HOME="$S")
    else
      echo "## mode=xdgcache (HOME=$S, XDG_STATE_HOME=$S/state, XDG_CACHE_HOME=$S/cache)"
      ENVV=(env HOME="$S" XDG_STATE_HOME="$S/state" XDG_CACHE_HOME="$S/cache")
    fi
    echo "### cargo test --lib"
    "${ENVV[@]}" "$CARGO" test --lib 2>&1 | grep -E '^test result|^running|FAILED|panicked'
    echo "### cargo test --test certification"
    "${ENVV[@]}" "$CARGO" test --test certification 2>&1 | grep -E '^test |^test result|^running|FAILED|panicked'
  done
} > "$OUT" 2>&1
grep -E '^## |^### |^test result' "$OUT"
