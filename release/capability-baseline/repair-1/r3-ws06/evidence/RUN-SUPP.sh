#!/usr/bin/env bash
# P2-AR-0037 — run SUPP-ws06-r3.py against the gov of <tree>, through the round-2 integration's root-channel evidence
# adapter (UNEDITED; it relays the owner-signed answer of S9 and passes every other invocation through byte-for-byte).
#   RUN-SUPP.sh <tree> <outfile>        Scratch: $P2AR0037_SCRATCH (required).
set -u
TREE="$(cd "${1:?tree}" && pwd)"; OUT="${2:?outfile}"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRB="${P2AR0037_SCRATCH:?set P2AR0037_SCRATCH}"; mkdir -p "$SCRB"
S="$(mktemp -d "$SCRB/supp-XXXXXX")"
R="$TREE/release/capability-baseline/repair-1"
export PYTHONDONTWRITEBYTECODE=1
for v in $(env | sed -n 's/^\(GOV_[A-Z_]*\)=.*/\1/p'); do unset "$v"; done
cat > "$S/gov" <<EOS
#!/usr/bin/env bash
export P2AR0022_REAL_GOV="$TREE/target/release/gov"
export P2AR0022_HC_OWNER="$R/ws03/evidence/hc_owner.py"
export P2AR0022_SHIM_LOG="$OUT.shimlog"
exec python3 "$R/integration-2/evidence/builder-probes/derived/gov-owner-channel-shim.root-channel.P2-AR-0032.py" "\$@"
EOS
chmod +x "$S/gov"
: > "$OUT.shimlog"
{
  echo "# P2-AR-0037 SUPP-ws06-r3 (sha256 $(sha256sum "$HERE/SUPP-ws06-r3.py" | cut -c1-64)) against $TREE"
  echo "# tree HEAD $(git -C "$TREE" rev-parse HEAD 2>/dev/null || echo '(git archive export of 53897c1)'); gov sha256 $(sha256sum "$TREE/target/release/gov" | cut -c1-64)"
  echo "# date $(date -u +%FT%TZ)"
} > "$OUT"
( export TMPDIR="$S"; GOV="$S/gov" SUPP_SCRATCH="$S" WT="$TREE" timeout 1500 python3 "$HERE/SUPP-ws06-r3.py" ) >> "$OUT" 2>&1
echo "[exit=$?]" >> "$OUT"
grep -E "^SUMMARY" "$OUT"
