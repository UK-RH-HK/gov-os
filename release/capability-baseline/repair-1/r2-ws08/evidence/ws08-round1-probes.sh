#!/usr/bin/env bash
# P2-AR-0029 (WS-8, round 2) — re-run the round-1 WS-8 builder probes (BC-P2-35..38, WS08-P1..P4) against one tree's
# target/release/gov, UNEDITED, the way the integration builder ran them (repair-1/integration/evidence/builder-probes/
# run-builder-probe.sh): WS08-P2 and WS08-P3 from repair-1/ws08/evidence/ through WS-3's role shim
# (repair-1/ws03/evidence/gov-role-shim.sh, which only declares `--role orchestrator` where an invocation declares no
# role); WS08-P1 and WS08-P4 as the integration builder's labelled derived owner-channel copies
# (repair-1/integration/evidence/builder-probes/derived-ws08/, header comments list each change), also through the
# role shim. Nothing is written beside any probe; outputs go to ws08-round1-probes-<label>/ here.
# Usage: ws08-round1-probes.sh <label> <tree>
set -u
LABEL="${1:?label}"; TREE="$(cd "${2:?tree}" && pwd)"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WT="$(cd "$HERE/../../../../.." && pwd)"
R="$WT/release/capability-baseline/repair-1"
SCR="${P2AR0029_SCRATCH:-$(cd "$WT/../.." && pwd)/p2-ar-0029-ws08probes}"
OUTD="$HERE/ws08-round1-probes-$LABEL"
mkdir -p "$OUTD" "$SCR"
export PYTHONDONTWRITEBYTECODE=1
for v in $(env | sed -n 's/^\(GOV_[A-Z_]*\)=.*/\1/p'); do unset "$v"; done
export WS03_REAL_GOV="$TREE/target/release/gov"
SHIM="$R/ws03/evidence/gov-role-shim.sh"
{
  echo "# P2-AR-0029 round-1 WS-8 probes, label=$LABEL, tree=$TREE"
  echo "# gov $WS03_REAL_GOV sha256 $(sha256sum "$WS03_REAL_GOV" | cut -d' ' -f1), invoked through $SHIM"
  echo "# date $(date -u +%FT%TZ)"
  for f in "$R"/ws08/evidence/WS08-P2-*.py "$R"/ws08/evidence/WS08-P3-*.py "$R"/integration/evidence/builder-probes/derived-ws08/*.py; do
    echo "  $(sha256sum "$f" | cut -d' ' -f1)  ${f#$WT/}"
  done
} > "$OUTD/00-header.out"
run() {  # run <name> <dir> <script>
  local name="$1" dir="$2" script="$3" t
  t="$(mktemp -d "$SCR/$LABEL-$name-XXXXXX")"
  ( cd "$dir" && GOV="$SHIM" PROBE_TMP="$t" timeout 900 python3 "$script" ) > "$OUTD/$name.out" 2>&1
  echo "[exit=$?]" >> "$OUTD/$name.out"
  grep -E '^SUMMARY' "$OUTD/$name.out" | sed "s|^|$name: |"
}
run WS08-P1 "$R/integration/evidence/builder-probes/derived-ws08" WS08-P1-post-install-integrity.py
run WS08-P2 "$R/ws08/evidence" WS08-P2-presentation.py
run WS08-P3 "$R/ws08/evidence" WS08-P3-certification-and-lock-identity.py
run WS08-P4 "$R/integration/evidence/builder-probes/derived-ws08" WS08-P4-rollback-and-atomicity.py
