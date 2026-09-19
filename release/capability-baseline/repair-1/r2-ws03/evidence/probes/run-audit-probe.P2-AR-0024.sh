#!/usr/bin/env bash
# P2-AR-0024 (WS-3 round 2) — DERIVED from the integration builder's runner (P2-AR-0022): re-run audit-of-record probes
# (release/capability-baseline/audit-0/<family>/evidence/), UNEDITED, against THIS worktree's binary. Changes: output
# goes to this directory (./audit-<mode>/), the scratch mirror is private to this run (P2AR0024_SCRATCH), and the shim
# is the integration builder's gov-owner-channel-shim.py used read-only from its directory.
#   integrated  the real integrated target/release/gov, each family's own invocation convention
#   shim        the same probe file, reached through a scratch mirror root whose entries are symlinks to this worktree
#               except target/release/gov, which runs gov-owner-channel-shim.py (adapts only role declaration, the
#               pre-WS-3 human-answer relay and missing gate-package fields; see that file). abspath keeps the mirror
#               path, so path-resolving harnesses (zprobe, govprobe via GOV_WT, lib.sh) use the adapter.
# Usage: P2AR0024_SCRATCH=<private dir> run-audit-probe.P2-AR-0024.sh <mode> <family> <probe> [<probe> ...]
#   family: alpha-r beta-r gamma-r delta-r epsilon-r zeta-r synthesis   probe: file name without extension
set -u
MODE="${1:?mode}"; FAM="${2:?family}"; shift 2
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WT="$(cd "$HERE/../../../../../.." && pwd)"
SCRB="${P2AR0024_SCRATCH:?set P2AR0024_SCRATCH}"; mkdir -p "$SCRB"
export PYTHONDONTWRITEBYTECODE=1
for v in $(env | sed -n 's/^\(GOV_[A-Z_]*\)=.*/\1/p'); do unset "$v"; done
unset GOV WT_OVERRIDE
if [ "$MODE" = shim ]; then
  ROOT="$SCRB/mirror-shim"
  if [ ! -x "$ROOT/target/release/gov" ]; then
    mkdir -p "$ROOT/target/release"
    for e in $(ls -A "$WT"); do [ "$e" = target ] || ln -sfn "$WT/$e" "$ROOT/$e"; done
    cat > "$ROOT/target/release/gov" <<EOF
#!/usr/bin/env bash
export P2AR0022_REAL_GOV="$WT/target/release/gov"
export P2AR0022_HC_OWNER="$WT/release/capability-baseline/repair-1/ws03/evidence/hc_owner.py"
exec python3 "$WT/release/capability-baseline/repair-1/integration/evidence/audit-probes/gov-owner-channel-shim.py" "\$@"
EOF
    chmod +x "$ROOT/target/release/gov"
  fi
else
  ROOT="$WT"
fi
BIN="$ROOT/target/release/gov"
EVD="$ROOT/release/capability-baseline/audit-0/$FAM/evidence"
OUTD="$HERE/audit-$MODE"; mkdir -p "$OUTD"
for P in "$@"; do
  S="$(mktemp -d "$SCRB/ap-$MODE-$FAM-$P-XXXXXX")"; mkdir -p "$S/tmp"
  OUT="$OUTD/$FAM.$P.out"
  {
    echo "# P2-AR-0024 audit-of-record probe re-run (unedited): $FAM/$P mode=$MODE"
    echo "# worktree HEAD $(git -C "$WT" rev-parse HEAD); product files differing from HEAD: $(git -C "$WT" status --porcelain -- runtime cli framework migrations tools Cargo.toml Cargo.lock | wc -l)"
    echo "# probe sha256 $(sha256sum "$WT/release/capability-baseline/audit-0/$FAM/evidence/$P."* 2>/dev/null | cut -c1-64 | head -1); gov $(sha256sum "$WT/target/release/gov" | cut -c1-64) via $BIN"
    echo "# date $(date -u +%FT%TZ)"
  } > "$OUT"
  if [ "$MODE" = shim ]; then export P2AR0022_SHIM_LOG="$OUT.shimlog"; : > "$P2AR0022_SHIM_LOG"; fi
  (
    cd "$EVD" || exit 9
    export TMPDIR="$S/tmp"
    case "$FAM" in
      zeta-r)    ZPROBE_SCRATCH="$S" timeout 900 python3 "$EVD/$P.py" ;;
      beta-r)    GOV_WT="$ROOT" PROBE_TMP="$S" timeout 900 python3 "$EVD/$P.py" ;;
      synthesis) if [ -f "$EVD/$P.py" ]; then GOV_BIN="$BIN" SYNTH_SCRATCH="$S" timeout 900 python3 "$EVD/$P.py"; else GOV="$BIN" GOV_BIN="$BIN" WT="$ROOT" SCRATCH="$S" timeout 900 bash "$EVD/$P.sh"; fi ;;
      delta-r)   GOV_BIN="$BIN" PROBE_SCRATCH="$S" timeout 900 python3 "$EVD/$P.py" ;;
      alpha-r)   if [ -f "$EVD/$P.py" ]; then GOV="$BIN" PROBE_TMP="$S" timeout 900 python3 "$EVD/$P.py"; else GOV="$BIN" WT="$ROOT" PROBE_TMP="$S" timeout 900 bash "$EVD/$P.sh"; fi ;;
      gamma-r)   if [ -f "$EVD/$P.sh" ]; then GOV="$BIN" WT="$ROOT" PROBES="$S" timeout 900 bash "$EVD/$P.sh"; else GOV="$BIN" GOV_BIN="$BIN" WT="$ROOT" PROBE_TMP="$S" timeout 900 python3 "$EVD/$P.py"; fi ;;
      epsilon-r) if [ -f "$EVD/$P.sh" ]; then GOV="$BIN" WT="$ROOT" SCRATCH="$S" timeout 900 bash "$EVD/$P.sh"; else GOV="$BIN" WT="$ROOT" SCRATCH="$S" timeout 900 python3 "$EVD/$P.py"; fi ;;
      *) echo "unknown family $FAM"; exit 2 ;;
    esac
  ) >> "$OUT" 2>&1
  echo "[exit=$?]" >> "$OUT"
  printf '%-10s %-45s %s\n' "$FAM" "$P" "$(grep -cE '(^|\s)(PASS)(\s|:|$)|\[PASS\]' "$OUT") pass-marks, $(grep -cE '(^|\s)(FAIL)(\s|:|$)|\[FAIL\]' "$OUT") fail-marks, $(grep -c Traceback "$OUT") tracebacks, $(tail -1 "$OUT")"
done
