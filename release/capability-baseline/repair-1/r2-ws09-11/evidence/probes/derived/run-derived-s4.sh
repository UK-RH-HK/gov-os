#!/usr/bin/env bash
# P2-AR-0030 — run the DERIVED copy of alpha-r S4-adopt-end-to-end.py (derived-S4-adopt-end-to-end.r2-roles.P2-AR-0030.py.txt)
# against one tree's gov through the round-1 integration's owner-channel/role adapter (see ../run-probe.sh), from a scratch
# mirror root whose alpha-r lib/ and fixtures/ resolve to that tree. Output: ./<tree>-shim/alpha-r.S4-adopt-end-to-end.derived[.raw-sql].out
# Usage: P2AR0030_SCRATCH=<dir> P2AR0030_BASE_TREE=<dir> run-derived-s4.sh <after|before> [raw-sql]
set -u
TREE="${1:?tree}"; RAW="${2:-}"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WT="$(cd "$HERE/../../../../../../.." && pwd)"
SCRB="${P2AR0030_SCRATCH:?}"
case "$TREE" in after) ROOT="$WT" ;; before) ROOT="${P2AR0030_BASE_TREE:?}" ;; *) exit 2 ;; esac
export PYTHONDONTWRITEBYTECODE=1
for v in $(env | sed -n 's/^\(GOV_[A-Z_]*\)=.*/\1/p'); do unset "$v"; done
M="$(mktemp -d "$SCRB/mirror-s4-$TREE-XXXXXX")"
for e in $(ls -A "$ROOT"); do [ "$e" = release ] || ln -sfn "$ROOT/$e" "$M/$e"; done
EVD="$M/release/capability-baseline/audit-0/alpha-r/evidence"; mkdir -p "$EVD"
ln -sfn "$ROOT/release/capability-baseline/audit-0/alpha-r/evidence/lib" "$EVD/lib"
cp "$HERE/derived-S4-adopt-end-to-end.r2-roles.P2-AR-0030.py.txt" "$EVD/derived_s4.py"
W="$SCRB/shim-$TREE"; mkdir -p "$W"
cat > "$W/gov" <<EOF
#!/usr/bin/env bash
export P2AR0022_REAL_GOV="$ROOT/target/release/gov"
export P2AR0022_HC_OWNER="$WT/release/capability-baseline/repair-1/ws03/evidence/hc_owner.py"
exec python3 "$WT/release/capability-baseline/repair-1/integration/evidence/audit-probes/gov-owner-channel-shim.py" "\$@"
EOF
chmod +x "$W/gov"
OUTD="$HERE/$TREE-shim"; mkdir -p "$OUTD"
OUT="$OUTD/alpha-r.S4-adopt-end-to-end.derived${RAW:+.raw-sql}.out"
S="$(mktemp -d "$SCRB/p-derived-s4-$TREE-XXXXXX")"
{ echo "# P2-AR-0030 DERIVED S4-adopt-end-to-end (see header of the .py.txt) tree=$TREE ${RAW:+RAW_SQL_STORE=1}"; echo "# gov $(sha256sum "$ROOT/target/release/gov" | cut -c1-64) via adapter"; echo "# date $(date -u +%FT%TZ)"; } > "$OUT"
export P2AR0022_SHIM_LOG="$OUT.shimlog"; : > "$P2AR0022_SHIM_LOG"
( cd "$EVD" && if [ -n "$RAW" ]; then export RAW_SQL_STORE=1; fi; GOV="$W/gov" PROBE_TMP="$S" timeout 1800 python3 "$EVD/derived_s4.py" ) >> "$OUT" 2>&1
echo "# exit $?" >> "$OUT"
echo "$OUT"
