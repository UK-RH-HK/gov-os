#!/usr/bin/env bash
# P2-AR-0035 (WS-4, repair-1 round 3) — re-run audit-of-record probes UNEDITED against a chosen gov binary.
#
# Derived from release/capability-baseline/repair-1/r2-ws04/evidence/run-probe.sh (P2-AR-0025), with ONE change: the
# adapter is the round-2 integration's labelled derived adapter
#   repair-1/integration-2/evidence/builder-probes/derived/gov-adapter.ws05.root-channel.P2-AR-0032.py (unedited),
# i.e. WS-5's evidence adapter (adaptations (a)-(e): role declaration, owner-signed relay of an already-rendered gate,
# absent package fields, receipt completion of ABSENT W5 fields, bare `passed` -> not_applicable_with_reason) with the
# human channel on the provisioned throw-away root instead of the standalone anchor P2-ADJ-0001 turned off. Both the
# "base" and the "after" run go through the same adapter, so every before/after pair differs only in the binary.
#
#   base   root = a read-only `git archive` export of the base commit 53897c1 (the integrated round-2 tree), with the
#          adapter running the base binary built from that export ($P2AR0035_BASE_GOV)
#   after  root = a private mirror of THIS worktree (symlinks to every entry except target/), with the adapter running
#          this worktree's target/debug/gov
#
# Usage: P2AR0035_SCRATCH=<dir> P2AR0035_BASE_GOV=<base gov> run-probe.sh <base|after> <family> <probe> [<probe> ...]
# Output: evidence/audit-probes/<mode>/<family>.<probe>.out (+ .shimlog). Probe files are never edited; their sha256 is
# logged.
set -u
MODE="${1:?mode}"; FAM="${2:?family}"; shift 2
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WT="$(git -C "$HERE" rev-parse --show-toplevel)"
SCRB="${P2AR0035_SCRATCH:?set P2AR0035_SCRATCH}"
export PYTHONDONTWRITEBYTECODE=1
for v in $(env | sed -n 's/^\(GOV_[A-Z_]*\)=.*/\1/p'); do unset "$v"; done
unset GOV WT_OVERRIDE
case "$MODE" in
  base)
    ROOT="$SCRB/probe-base-tree"
    REAL="${P2AR0035_BASE_GOV:?set P2AR0035_BASE_GOV}"
    if [ ! -d "$ROOT" ]; then
      mkdir -p "$ROOT"; git -C "$WT" archive 53897c1a44157e5af81b176017bc7ded6a63b9cd | tar -x -C "$ROOT"
    fi
    ;;
  after)
    ROOT="$SCRB/probe-mirror-after"
    REAL="$WT/target/debug/gov"
    if [ ! -d "$ROOT" ]; then
      mkdir -p "$ROOT"
      for e in $(ls -A "$WT"); do [ "$e" = target ] || ln -sfn "$WT/$e" "$ROOT/$e"; done
    fi
    ;;
  *) echo "mode must be base|after"; exit 2 ;;
esac
ADAPTER="$ROOT/release/capability-baseline/repair-1/integration-2/evidence/builder-probes/derived/gov-adapter.ws05.root-channel.P2-AR-0032.py"
HC="$ROOT/release/capability-baseline/repair-1/ws03/evidence/hc_owner.py"
mkdir -p "$ROOT/target/release"
cat > "$ROOT/target/release/gov" <<EOF
#!/usr/bin/env bash
export P2AR0026_REAL_GOV="$REAL"
export P2AR0026_HC_OWNER="$HC"
exec python3 "$ADAPTER" "\$@"
EOF
chmod +x "$ROOT/target/release/gov"
BIN="$ROOT/target/release/gov"
EVD="$ROOT/release/capability-baseline/audit-0/$FAM/evidence"
OUTD="$HERE/$MODE"; mkdir -p "$OUTD"
for P in "$@"; do
  S="$(mktemp -d "$SCRB/pr-$MODE-$FAM-$P-XXXXXX")"; mkdir -p "$S/tmp"
  OUT="$OUTD/$FAM.$P.out"
  {
    echo "# P2-AR-0035 audit-of-record probe re-run (unedited, through the P2-AR-0032 root-channel adapter): $FAM/$P mode=$MODE"
    echo "# worktree HEAD $(git -C "$WT" rev-parse HEAD); product files differing from HEAD: $(git -C "$WT" status --porcelain -- runtime cli framework migrations Cargo.toml Cargo.lock | wc -l)"
    echo "# probe sha256 $(sha256sum "$EVD/$P."* 2>/dev/null | grep -v '\.out$' | cut -c1-64 | head -1); real gov $(sha256sum "$REAL" | cut -c1-64) ($REAL)"
    echo "# adapter sha256 $(sha256sum "$ADAPTER" | cut -c1-64)"
    echo "# date $(date -u +%FT%TZ)"
  } > "$OUT"
  export P2AR0026_SHIM_LOG="$OUT.shimlog"; : > "$P2AR0026_SHIM_LOG"
  (
    cd "$EVD" || exit 9
    export TMPDIR="$S/tmp"
    case "$FAM" in
      zeta-r)    ZPROBE_SCRATCH="$S" timeout 1500 python3 "$EVD/$P.py" ;;
      beta-r)    GOV_WT="$ROOT" PROBE_TMP="$S" timeout 1500 python3 "$EVD/$P.py" ;;
      synthesis) if [ -f "$EVD/$P.py" ]; then GOV_BIN="$BIN" SYNTH_SCRATCH="$S" timeout 1500 python3 "$EVD/$P.py"; else GOV="$BIN" GOV_BIN="$BIN" WT="$ROOT" SCRATCH="$S" timeout 1500 bash "$EVD/$P.sh"; fi ;;
      delta-r)   GOV_BIN="$BIN" PROBE_SCRATCH="$S" timeout 1500 python3 "$EVD/$P.py" ;;
      gamma-r)   if [ -f "$EVD/$P.sh" ]; then GOV="$BIN" WT="$ROOT" PROBES="$S" timeout 1500 bash "$EVD/$P.sh"; else GOV="$BIN" GOV_BIN="$BIN" WT="$ROOT" PROBE_TMP="$S" timeout 1500 python3 "$EVD/$P.py"; fi ;;
      *) echo "unknown family $FAM"; exit 2 ;;
    esac
  ) >> "$OUT" 2>&1
  echo "[exit=$?]" >> "$OUT"
  printf '%-6s %-10s %-40s %s\n' "$MODE" "$FAM" "$P" "$(grep -cE '(^|\s)(PASS)(\s|:|$)|\[PASS\]' "$OUT") pass-marks, $(grep -cE '(^|\s)(FAIL)(\s|:|$)|\[FAIL\]' "$OUT") fail-marks, $(grep -c Traceback "$OUT") tracebacks, $(tail -1 "$OUT")"
done
