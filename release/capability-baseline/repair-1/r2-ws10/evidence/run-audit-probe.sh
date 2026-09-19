#!/usr/bin/env bash
# P2-AR-0031 (WS-10, round 2) — re-run audit-of-record probes (release/capability-baseline/audit-0/<family>/evidence/),
# UNEDITED, against a chosen gov binary and a chosen source tree. Derived from the integration builder's runner
# (repair-1/integration/evidence/audit-probes/run-audit-probe.sh, P2-AR-0022); the only differences: the binary, the
# tree and the output directory are parameters, and every scratch path is private to this run (P2AR0031_SCRATCH).
#   mode integrated  the probe runs against GOV_UNDER_TEST directly, from TREE's audit-0 evidence directory
#   mode shim        the same unedited probe file, reached through a private mirror root (symlinks to TREE) whose
#                    target/release/gov runs the integration's unedited evidence adapter gov-owner-channel-shim.py
#                    (it adapts ONLY role declaration, the pre-WS-3 human-answer relay and absent gate-package fields)
#                    with the real binary GOV_UNDER_TEST.
# Usage: P2AR0031_SCRATCH=<dir> GOV_UNDER_TEST=<gov> TREE=<source tree> OUTD=<dir> run-audit-probe.sh <mode> <family> <probe>...
set -u
MODE="${1:?mode}"; FAM="${2:?family}"; shift 2
SCRB="${P2AR0031_SCRATCH:?set P2AR0031_SCRATCH}"
REALGOV="${GOV_UNDER_TEST:?set GOV_UNDER_TEST}"
TREE="${TREE:?set TREE}"
OUTD="${OUTD:?set OUTD}"; mkdir -p "$OUTD"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WT="$(cd "$HERE/../../../../.." && pwd)"
SHIM="$WT/release/capability-baseline/repair-1/integration/evidence/audit-probes/gov-owner-channel-shim.py"
HCO="$WT/release/capability-baseline/repair-1/ws03/evidence/hc_owner.py"
export PYTHONDONTWRITEBYTECODE=1
for v in $(env | sed -n 's/^\(GOV_[A-Z_]*\)=.*/\1/p'); do [ "$v" = GOV_UNDER_TEST ] || unset "$v"; done
unset GOV WT_OVERRIDE
TAG="$(basename "$OUTD")"
ROOT="$SCRB/mirror-$MODE-$TAG"
mkdir -p "$ROOT/target/release"
for e in $(ls -A "$TREE"); do [ "$e" = target ] || ln -sfn "$TREE/$e" "$ROOT/$e"; done
if [ "$MODE" = shim ]; then
  cat > "$ROOT/target/release/gov" <<EOS
#!/usr/bin/env bash
export P2AR0022_REAL_GOV="$REALGOV"
export P2AR0022_HC_OWNER="$HCO"
exec python3 "$SHIM" "\$@"
EOS
  chmod +x "$ROOT/target/release/gov"
else
  ln -sfn "$REALGOV" "$ROOT/target/release/gov"
fi
BIN="$ROOT/target/release/gov"
EVD="$ROOT/release/capability-baseline/audit-0/$FAM/evidence"
for P in "$@"; do
  S="$(mktemp -d "$SCRB/ap-$MODE-$TAG-$FAM-$P-XXXXXX")"; mkdir -p "$S/tmp"
  OUT="$OUTD/$FAM.$P.$MODE.out"
  {
    echo "# P2-AR-0031 audit-of-record probe re-run (unedited): $FAM/$P mode=$MODE"
    echo "# tree $TREE (HEAD $(git -C "$TREE" rev-parse HEAD 2>/dev/null || echo n/a)); product files differing from HEAD: $(git -C "$TREE" status --porcelain -- runtime cli framework migrations tools Cargo.toml Cargo.lock 2>/dev/null | wc -l)"
    echo "# probe sha256 $(sha256sum "$TREE/release/capability-baseline/audit-0/$FAM/evidence/$P."* 2>/dev/null | cut -c1-64 | head -1); gov $(sha256sum "$REALGOV" | cut -c1-64) via $BIN"
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
