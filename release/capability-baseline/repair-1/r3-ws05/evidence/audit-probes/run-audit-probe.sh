#!/usr/bin/env bash
# P2-AR-0036 — re-run audit-of-record probes (release/capability-baseline/audit-0/<family>/evidence/), UNEDITED, against
# this worktree's binary and against the round-3 base binary (negative control: the integrated round-2 tree 53897c1 built
# in scratch), in one of four modes; output to ./<mode>/<family>.<probe>.out only. DERIVED COPY of WS-5's round-2 runner
# (repair-1/r2-ws05/evidence/audit-probes/run-audit-probe.sh, P2-AR-0026). Changes, and nothing else: the run id and
# environment names (P2AR0036_*), and the evidence adapter is the round-2 integration builder's root-channel copy of
# that runner's adapter (repair-1/integration-2/evidence/builder-probes/derived/gov-adapter.ws05.root-channel.P2-AR-0032.py,
# referenced in place, unmodified) because P2-ADJ-0001 turned the standalone human-channel anchor off. The family
# invocation conventions are unchanged. Base modes mirror the BASE TREE (the scratch export of 53897c1 whose build is
# $P2AR0036_BASE_GOV; default: two directories above that binary's target/release), not this worktree, so the base binary
# is paired with its own framework payload (an `init --source <root>/framework` against this worktree's changed framework
# is correctly refused by the base binary as an external source, which would mask the base behaviour).
#   after       this worktree's target/release/gov, each family's own invocation convention (unedited, no adapter)
#   after-shim  the same probe file, reached through a scratch mirror root whose entries are symlinks to this worktree
#               except target/release/gov, which runs gov-adapter.py (evidence adapter; adapts only role declaration,
#               the pre-WS-3 human-answer relay, missing gate-package fields and — new here — a close report that
#               lacks the W5 receipt fields; see that file) over this worktree's binary
#   base        the round-3 base binary ($P2AR0036_BASE_GOV: the integrated round-2 tree 53897c1 built in scratch),
#               unedited, through a mirror whose target/release/gov is that binary
#   base-shim   the base binary through the same adapter
# Usage: P2AR0036_SCRATCH=<dir> [P2AR0036_BASE_GOV=<gov>] run-audit-probe.sh <mode> <family> <probe> [<probe> ...]
#   family: alpha-r beta-r gamma-r delta-r epsilon-r zeta-r synthesis   probe: file name without extension
set -u
MODE="${1:?mode}"; FAM="${2:?family}"; shift 2
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WT="$(cd "$HERE/../../../../../.." && pwd)"
SCRB="${P2AR0036_SCRATCH:?set P2AR0036_SCRATCH}"
export PYTHONDONTWRITEBYTECODE=1
for v in $(env | sed -n 's/^\(GOV_[A-Z_]*\)=.*/\1/p'); do unset "$v"; done
unset GOV WT_OVERRIDE
mirror() {  # $1 = mirror dir, $2 = real gov, $3 = adapter|direct, $4 = tree the mirror links to
  local ROOTM="$1" REALG="$2" KIND="$3" SRC="$4"
  if [ ! -e "$ROOTM/target/release/gov" ]; then
    mkdir -p "$ROOTM/target/release"
    for e in $(ls -A "$SRC"); do [ "$e" = target ] || [ "$e" = .git ] || ln -sfn "$SRC/$e" "$ROOTM/$e"; done
    if [ "$KIND" = adapter ]; then
      cat > "$ROOTM/target/release/gov" <<EOF
#!/usr/bin/env bash
export P2AR0026_REAL_GOV="$REALG"
export P2AR0026_HC_OWNER="$WT/release/capability-baseline/repair-1/ws03/evidence/hc_owner.py"
exec python3 "$WT/release/capability-baseline/repair-1/integration-2/evidence/builder-probes/derived/gov-adapter.ws05.root-channel.P2-AR-0032.py" "\$@"
EOF
      chmod +x "$ROOTM/target/release/gov"
    else
      ln -sfn "$REALG" "$ROOTM/target/release/gov"
    fi
  fi
  echo "$ROOTM"
}
case "$MODE" in
  after)     ROOT="$WT"; REAL="$WT/target/release/gov" ;;
  after-shim) REAL="$WT/target/release/gov"; ROOT="$(mirror "$SCRB/mirror-after-shim" "$REAL" adapter "$WT")" ;;
  base)      REAL="${P2AR0036_BASE_GOV:?set P2AR0036_BASE_GOV}"; BT="${P2AR0036_BASE_TREE:-$(cd "$(dirname "$REAL")/../.." && pwd)}"
             ROOT="$(mirror "$SCRB/mirror-base" "$REAL" direct "$BT")" ;;
  base-shim) REAL="${P2AR0036_BASE_GOV:?set P2AR0036_BASE_GOV}"; BT="${P2AR0036_BASE_TREE:-$(cd "$(dirname "$REAL")/../.." && pwd)}"
             ROOT="$(mirror "$SCRB/mirror-base-shim" "$REAL" adapter "$BT")" ;;
  *) echo "unknown mode $MODE"; exit 2 ;;
esac
BIN="$ROOT/target/release/gov"
EVD="$ROOT/release/capability-baseline/audit-0/$FAM/evidence"
OUTD="$HERE/$MODE"; mkdir -p "$OUTD"
for P in "$@"; do
  S="$(mktemp -d "$SCRB/ap-$MODE-$FAM-$P-XXXXXX")"; mkdir -p "$S/tmp"
  OUT="$OUTD/$FAM.$P.out"
  {
    echo "# P2-AR-0036 audit-of-record probe re-run (unedited): $FAM/$P mode=$MODE"
    echo "# worktree HEAD $(git -C "$WT" rev-parse HEAD); product files differing from HEAD: $(git -C "$WT" status --porcelain -- runtime cli framework migrations tools Cargo.toml Cargo.lock | wc -l)"
    echo "# probe sha256 $(sha256sum "$WT/release/capability-baseline/audit-0/$FAM/evidence/$P."* 2>/dev/null | cut -c1-64 | head -1); real gov $(sha256sum "$REAL" | cut -c1-64) via $BIN"
    echo "# date $(date -u +%FT%TZ)"
  } > "$OUT"
  case "$MODE" in *shim) export P2AR0026_SHIM_LOG="$OUT.shimlog"; : > "$P2AR0026_SHIM_LOG" ;; esac
  (
    cd "$EVD" || exit 9
    export TMPDIR="$S/tmp"
    case "$FAM" in
      zeta-r)    ZPROBE_SCRATCH="$S" timeout 1200 python3 "$EVD/$P.py" ;;
      beta-r)    GOV_WT="$ROOT" PROBE_TMP="$S" timeout 1200 python3 "$EVD/$P.py" ;;
      synthesis) if [ -f "$EVD/$P.py" ]; then GOV_BIN="$BIN" SYNTH_SCRATCH="$S" timeout 1200 python3 "$EVD/$P.py"; else GOV="$BIN" GOV_BIN="$BIN" WT="$ROOT" SCRATCH="$S" timeout 1200 bash "$EVD/$P.sh"; fi ;;
      delta-r)   GOV_BIN="$BIN" PROBE_SCRATCH="$S" timeout 1200 python3 "$EVD/$P.py" ;;
      alpha-r)   if [ -f "$EVD/$P.py" ]; then GOV="$BIN" PROBE_TMP="$S" timeout 1200 python3 "$EVD/$P.py"; else GOV="$BIN" WT="$ROOT" PROBE_TMP="$S" timeout 1200 bash "$EVD/$P.sh"; fi ;;
      gamma-r)   if [ -f "$EVD/$P.sh" ]; then GOV="$BIN" WT="$ROOT" PROBES="$S" timeout 1200 bash "$EVD/$P.sh"; else GOV="$BIN" GOV_BIN="$BIN" WT="$ROOT" PROBE_TMP="$S" timeout 1200 python3 "$EVD/$P.py"; fi ;;
      epsilon-r) if [ -f "$EVD/$P.sh" ]; then GOV="$BIN" WT="$ROOT" SCRATCH="$S" timeout 1200 bash "$EVD/$P.sh"; else GOV="$BIN" WT="$ROOT" SCRATCH="$S" timeout 1200 python3 "$EVD/$P.py"; fi ;;
      *) echo "unknown family $FAM"; exit 2 ;;
    esac
  ) >> "$OUT" 2>&1
  echo "[exit=$?]" >> "$OUT"
  printf '%-10s %-10s %-45s %s\n' "$MODE" "$FAM" "$P" "$(grep -cE '(^|\s)(PASS)(\s|:|$)|\[PASS\]' "$OUT") pass-marks, $(grep -cE '(^|\s)(FAIL)(\s|:|$)|\[FAIL\]' "$OUT") fail-marks, $(grep -c Traceback "$OUT") tracebacks, $(tail -1 "$OUT")"
done
