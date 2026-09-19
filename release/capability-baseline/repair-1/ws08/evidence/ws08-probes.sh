#!/usr/bin/env bash
# P2-AR-0020 (WS-8) — run the four supplementary WS08 probes against one `gov` binary.
# Builder evidence only (Contract v3 O3). Run once against the repaired binary and once against the base commit's
# binary (negative control: the same attack still succeeds there, so each probe line discriminates).
# Usage: ws08-probes.sh <label> [gov-binary]   (writes ws08-probes-<label>.out beside this script)
set -u
LABEL="${1:?label}"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WT="$(cd "$HERE/../../../../.." && pwd)"
GOVBIN="${2:-$WT/target/release/gov}"
SCR="${P2AR0020_SCRATCH:?set P2AR0020_SCRATCH}"
OUT="$HERE/ws08-probes-$LABEL.out"
export PYTHONDONTWRITEBYTECODE=1 GOV="$GOVBIN"
for v in $(env | sed -n 's/^\(GOV_[A-Z_]*\)=.*/\1/p'); do [ "$v" = GOV ] || unset "$v"; done
{
  echo "# P2-AR-0020 WS08 probes, label=$LABEL"
  echo "# HEAD $(git -C "$WT" rev-parse HEAD) dirty-files: $(git -C "$WT" status --porcelain | wc -l) date $(date -u +%FT%TZ)"
  echo "# gov $GOVBIN sha256 $(sha256sum "$GOVBIN" | cut -d' ' -f1)"
  for p in WS08-P1-post-install-integrity.py WS08-P2-presentation.py WS08-P3-certification-and-lock-identity.py WS08-P4-rollback-and-atomicity.py; do
    t="$(mktemp -d "$SCR/ws08-$LABEL-XXXXXX")"
    echo; echo "=================== $p ==================="
    ( cd "$HERE" && PROBE_TMP="$t" timeout 900 python3 "$p" ) 2>&1
    echo "[$p exit=$?]"
  done
} > "$OUT" 2>&1
grep -E '^W |^SUMMARY|Traceback|exit=' "$OUT" | cut -c1-200
