#!/usr/bin/env bash
# P2-AR-0028 (WS-7, repair iteration 1 round 2) — re-run the audit-of-record probes the repair delta names for
# BC-P2-39/40/41/11(plugin)/09(registry), UNEDITED, against a given `gov` binary, in two modes:
#   unedited  the probe file as committed under release/capability-baseline/audit-0/, the binary as given
#   shim      the same unedited probe file, with `gov` reached through the round-1 integration builder's evidence adapter
#             release/capability-baseline/repair-1/integration/evidence/audit-probes/gov-owner-channel-shim.py
#             (unmodified; it adapts ONLY the three paths WS-3 removed by design: undeclared role -> orchestrator,
#             the pre-WS-3 `decide --by owner` relay -> an owner-signed answer through the human channel for a gate the
#             OS already rendered, and absent gate-package fields). Without it the probes stop at setup on every tree
#             after round 1 (see the integration report §8), so the plugin/tool lines cannot be reached.
# Nothing under audit-0/ is written: every probe writes to stdout (redirected here) and to a private scratch dir.
# Usage: P2AR0028_SCRATCH=<dir> run-probes.sh <label> <gov-binary>
set -u
LABEL="${1:?label}"; BIN="${2:?gov binary}"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WT="$(cd "$HERE/../../../../.." && pwd)"
SCR="${P2AR0028_SCRATCH:?set P2AR0028_SCRATCH}"
export PYTHONDONTWRITEBYTECODE=1
for v in $(env | sed -n 's/^\(GOV_[A-Z_]*\)=.*/\1/p'); do unset "$v"; done
GAMMA="$WT/release/capability-baseline/audit-0/gamma-r/evidence"
SYNTH="$WT/release/capability-baseline/audit-0/synthesis/evidence"
SHIM="$WT/release/capability-baseline/repair-1/integration/evidence/audit-probes/gov-owner-channel-shim.py"
HC="$WT/release/capability-baseline/repair-1/ws03/evidence/hc_owner.py"
mkdir -p "$SCR/bin-$LABEL"
WRAP="$SCR/bin-$LABEL/gov-shim"
cat > "$WRAP" <<EOF
#!/usr/bin/env bash
export P2AR0022_REAL_GOV="$BIN"
export P2AR0022_HC_OWNER="$HC"
exec python3 "$SHIM" "\$@"
EOF
chmod +x "$WRAP"
for MODE in unedited shim; do
  OUTD="$HERE/probes/$LABEL-$MODE"; mkdir -p "$OUTD"
  if [ "$MODE" = shim ]; then G="$WRAP"; else G="$BIN"; fi
  for P in F4-plugins F2F3-tools FRESH-invalidation; do
    S="$(mktemp -d "$SCR/pr-$LABEL-$MODE-$P-XXXXXX")"; mkdir -p "$S/tmp"
    OUT="$OUTD/gamma-r.$P.out"
    {
      echo "# P2-AR-0028 probe re-run: gamma-r/$P mode=$MODE label=$LABEL"
      echo "# worktree HEAD $(git -C "$WT" rev-parse HEAD); product files differing from HEAD: $(git -C "$WT" status --porcelain -- runtime cli framework capabilities tools Cargo.toml Cargo.lock | wc -l)"
      echo "# probe sha256 $(sha256sum "$GAMMA/$P.sh" | cut -c1-64); gov $(sha256sum "$BIN" | cut -c1-64) via $G"
    } > "$OUT"
    if [ "$MODE" = shim ]; then export P2AR0022_SHIM_LOG="$OUT.shimlog"; : > "$P2AR0022_SHIM_LOG"; else unset P2AR0022_SHIM_LOG; fi
    ( cd "$GAMMA" && TMPDIR="$S/tmp" GOV="$G" WT="$WT" PROBES="$S" timeout 900 bash "$GAMMA/$P.sh" ) >> "$OUT" 2>&1
    echo "[exit=$?]" >> "$OUT"
  done
  S="$(mktemp -d "$SCR/pr-$LABEL-$MODE-X4-XXXXXX")"; mkdir -p "$S/tmp"
  OUT="$OUTD/synthesis.LEAD-X4-registered-module-plugin-unpinned.out"
  {
    echo "# P2-AR-0028 probe re-run: synthesis/LEAD-X4-registered-module-plugin-unpinned mode=$MODE label=$LABEL"
    echo "# gov $(sha256sum "$BIN" | cut -c1-64) via $G"
  } > "$OUT"
  if [ "$MODE" = shim ]; then export P2AR0022_SHIM_LOG="$OUT.shimlog"; : > "$P2AR0022_SHIM_LOG"; fi
  ( cd "$SYNTH" && TMPDIR="$S/tmp" GOV_BIN="$G" SYNTH_SCRATCH="$S" timeout 900 python3 "$SYNTH/LEAD-X4-registered-module-plugin-unpinned.py" ) >> "$OUT" 2>&1
  echo "[exit=$?]" >> "$OUT"
done
echo "done $LABEL"
