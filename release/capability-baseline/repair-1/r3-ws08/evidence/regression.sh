#!/usr/bin/env bash
# P2-AR-0039 (WS-8, repair iteration 1 round 3) — builder regression (Contract v3 O3: regression evidence only).
# Same method as WS-8's round-2 script (repair-1/r2-ws08/evidence/regression.sh):
#   mode default  : HOME redirected to a private scratch dir, XDG_* unset (a normal workstation layout), GOV_* stripped
#   mode xdgcache : HOME redirected, XDG_STATE_HOME/XDG_CACHE_HOME set to paths WITHOUT a ".cache" segment
#                   (the alpha-r 00-regression-variant-xdg-cache condition behind A0-A2-03)
#   part lib      : cargo test --lib
#   part cert-a   : cargo test --test certification, modules arch..repair (repair:: only); records `-- --list`
#   part cert-b   : modules repair2..upstream
#   part cert-c   : modules ws03..ws08_r3
# The certification suite is split only so each part fits one foreground command; the `--list` recorded with part
# cert-a lets the parts be checked to cover every test exactly once.
# Usage: regression.sh <label> <mode> <part>   (writes regression/regression-<label>-<mode>-<part>.out)
set -u
LABEL="${1:?label}"; MODE="${2:?mode}"; PART="${3:?part}"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WT="$(cd "$HERE/../../../../.." && pwd)"
mkdir -p "$HERE/regression"
OUT="$HERE/regression/regression-$LABEL-$MODE-$PART.out"
export CARGO_BUILD_JOBS=2
CARGO="${CARGO:-$HOME/.cargo/bin/cargo}"
SCR="${P2AR0039_SCRATCH:-$(cd "$WT/../.." && pwd)/p2-ar-0039-regression}"
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
B_FILTERS=(repair2:: repair3:: section6:: srr:: update:: upstream::)
C_FILTERS=(ws03:: ws04r2:: ws05:: ws06:: ws07:: ws08:: ws08_r2:: ws08_r3::)
{
  echo "# P2-AR-0039 regression, label=$LABEL mode=$MODE part=$PART"
  echo "# worktree $WT"
  echo "# HEAD $(git rev-parse HEAD)  product files differing from HEAD: $(git status --porcelain -- runtime cli framework migrations tools tests Cargo.toml Cargo.lock | wc -l)  date $(date -u +%FT%TZ)"
  echo "## mode=$MODE ($MDESC)"
  case "$PART" in
    lib)
      echo "### cargo test --lib"
      "${ENVV[@]}" "$CARGO" test --lib 2>&1 | grep -E '^test |^test result|^running|FAILED|panicked|^warning: unused|^error' ;;
    cert-a)
      echo "### cargo test --test certification -- --list"
      "${ENVV[@]}" "$CARGO" test --test certification -- --list 2>/dev/null | grep -E ': test$'
      echo "### cargo test --test certification -- ${A_FILTERS[*]}"
      "${ENVV[@]}" "$CARGO" test --test certification -- "${A_FILTERS[@]}" 2>&1 | grep -E '^test |^test result|^running|FAILED|panicked|^---- |^error' ;;
    cert-b)
      echo "### cargo test --test certification -- ${B_FILTERS[*]}"
      "${ENVV[@]}" "$CARGO" test --test certification -- "${B_FILTERS[@]}" 2>&1 | grep -E '^test |^test result|^running|FAILED|panicked|^---- |^error' ;;
    cert-c)
      echo "### cargo test --test certification -- ${C_FILTERS[*]}"
      "${ENVV[@]}" "$CARGO" test --test certification -- "${C_FILTERS[@]}" 2>&1 | grep -E '^test |^test result|^running|FAILED|panicked|^---- |^error' ;;
  esac
} > "$OUT" 2>&1
grep -E '^## |^### |^test result' "$OUT"
