#!/usr/bin/env bash
# P2-AR-0029 (WS-8, repair iteration 1 round 2) — builder regression (Contract v3 O3: regression evidence only).
#   mode default  : HOME redirected to a private scratch dir, XDG_* unset (a normal workstation layout), GOV_* stripped
#   mode xdgcache : HOME redirected, XDG_STATE_HOME/XDG_CACHE_HOME set to paths WITHOUT a ".cache" segment
#                   (the alpha-r 00-regression-variant-xdg-cache condition behind A0-A2-03)
#   part lib      : cargo test --lib
#   part cert-a   : cargo test --test certification, modules arch..repair (repair:: only)
#   part cert-b   : cargo test --test certification, modules repair2..ws08_r2
# The certification suite is split in two parts only so each part fits one foreground command on a loaded shared
# host; `cargo test --test certification -- --list` is recorded with part cert-a so the two parts can be checked to
# cover every test exactly once.
# Usage: regression.sh <label> <mode> <part>   (writes regression-<label>-<mode>-<part>.out beside this script)
set -u
LABEL="${1:?label}"; MODE="${2:?mode}"; PART="${3:?part}"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WT="$(cd "$HERE/../../../../.." && pwd)"
OUT="$HERE/regression-$LABEL-$MODE-$PART.out"
export CARGO_BUILD_JOBS=2
CARGO="${CARGO:-$HOME/.cargo/bin/cargo}"
SCR="${P2AR0029_SCRATCH:-$(cd "$WT/../.." && pwd)/p2-ar-0029-regression}"
mkdir -p "$SCR"
for v in $(env | sed -n 's/^\(GOV_[A-Z_]*\)=.*/\1/p'); do unset "$v"; done
cd "$WT" || exit 1
S="$(mktemp -d "$SCR/regress-$MODE-XXXXXX")"
if [ "$MODE" = default ]; then
  ENVV=(env -u XDG_STATE_HOME -u XDG_CACHE_HOME -u XDG_CONFIG_HOME HOME="$S" CARGO_HOME="$HOME/.cargo" RUSTUP_HOME="$HOME/.rustup")
  MDESC="HOME=$S, XDG_* unset"
else
  ENVV=(env HOME="$S" XDG_STATE_HOME="$S/state" XDG_CACHE_HOME="$S/cache" CARGO_HOME="$HOME/.cargo" RUSTUP_HOME="$HOME/.rustup")
  MDESC="HOME=$S, XDG_STATE_HOME=$S/state, XDG_CACHE_HOME=$S/cache"
fi
A_FILTERS=(arch:: brownfield:: failure_injection:: greenfield:: migration:: multi_machine:: repair::)
B_FILTERS=(repair2:: repair3:: section6:: srr:: update:: upstream:: ws03:: ws08:: ws08_r2::)
{
  echo "# P2-AR-0029 regression, label=$LABEL mode=$MODE part=$PART"
  echo "# worktree $WT"
  echo "# HEAD $(git rev-parse HEAD)  dirty-files: $(git status --porcelain | wc -l)  date $(date -u +%FT%TZ)"
  echo "## mode=$MODE ($MDESC)"
  case "$PART" in
    lib)
      echo "### cargo test --lib"
      "${ENVV[@]}" "$CARGO" test --lib 2>&1 | grep -E '^test |^test result|^running|FAILED|panicked' ;;
    cert-a)
      echo "### cargo test --test certification -- --list"
      "${ENVV[@]}" "$CARGO" test --test certification -- --list 2>/dev/null | grep -E ': test$'
      echo "### cargo test --test certification -- ${A_FILTERS[*]}"
      "${ENVV[@]}" "$CARGO" test --test certification -- "${A_FILTERS[@]}" 2>&1 | grep -E '^test |^test result|^running|FAILED|panicked|^---- ' ;;
    cert-b)
      echo "### cargo test --test certification -- ${B_FILTERS[*]}"
      "${ENVV[@]}" "$CARGO" test --test certification -- "${B_FILTERS[@]}" 2>&1 | grep -E '^test |^test result|^running|FAILED|panicked|^---- ' ;;
  esac
} > "$OUT" 2>&1
grep -E '^## |^### |^test result' "$OUT"
