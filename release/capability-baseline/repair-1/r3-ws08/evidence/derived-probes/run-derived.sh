#!/usr/bin/env bash
# P2-AR-0039 — run the labelled DERIVED probe copies (derive_probes.py) against one tree, exactly as probes-rerun.sh runs
# the unedited probes: through a scratch MIRROR of the tree whose target/release/gov is the integration builder's
# evidence adapter (role declaration and owner-signed relay only; every lifecycle ingress reaches the real binary
# byte-for-byte). The probe library is the tree's own (ALPHA_R_LIB inside the mirror), so REPO, HEAD and the shipped
# releases are the tree under test.
# Usage: run-derived.sh <label> <tree>   (writes derived-<label>/<probe>.out beside this script)
set -u
LABEL="${1:?label}"; TREE="$(cd "${2:?tree}" && pwd)"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WT="$(cd "$HERE/../../../../../.." && pwd)"
SCR="${P2AR0039_SCRATCH:-$(cd "$WT/../.." && pwd)/p2-ar-0039-probes}"
OUTD="$HERE/derived-$LABEL"
GEN="$SCR/derived-src-$LABEL"
mkdir -p "$OUTD" "$SCR" "$GEN"
export PYTHONDONTWRITEBYTECODE=1
for v in $(env | sed -n 's/^\(GOV_[A-Z_]*\)=.*/\1/p'); do unset "$v"; done
python3 "$HERE/derive_probes.py" "$GEN" > "$OUTD/00-derivation-diff.out" 2>&1 || { cat "$OUTD/00-derivation-diff.out"; exit 1; }
MIRROR="$SCR/mirror-$LABEL"
if [ ! -x "$MIRROR/target/release/gov" ]; then
  mkdir -p "$MIRROR/target/release"
  for e in $(ls -A "$TREE"); do [ "$e" = target ] || ln -sfn "$TREE/$e" "$MIRROR/$e"; done
  cat > "$MIRROR/target/release/gov" <<EOF2
#!/usr/bin/env bash
export P2AR0022_REAL_GOV="$TREE/target/release/gov"
export P2AR0022_HC_OWNER="$WT/release/capability-baseline/repair-1/ws03/evidence/hc_owner.py"
exec python3 "$WT/release/capability-baseline/repair-1/integration/evidence/audit-probes/gov-owner-channel-shim.py" "\$@"
EOF2
  chmod +x "$MIRROR/target/release/gov"
fi
LIB="$MIRROR/release/capability-baseline/audit-0/alpha-r/evidence/lib"
{
  echo "# P2-AR-0039 derived-probe run label=$LABEL"
  echo "# tree $TREE (HEAD $(git -C "$TREE" rev-parse HEAD 2>/dev/null); tree KERNEL.yaml version $(sed -n 's/^version: //p' "$TREE/framework/KERNEL.yaml"))"
  echo "# date $(date -u +%FT%TZ)"
  echo "# gov $TREE/target/release/gov sha256 $(sha256sum "$TREE/target/release/gov" | cut -d' ' -f1) (reached via the evidence adapter)"
  echo "# derived sources (sha256):"
  for f in "$GEN"/*.py "$HERE"/*.provisioned.P2-AR-0039.py; do echo "  $(sha256sum "$f" | cut -d' ' -f1)  $(basename "$f")"; done
  echo "# the derivation (diff against the audit-of-record files) is in 00-derivation-diff.out"
} > "$OUTD/00-header.out"
for f in "$GEN"/*.py "$HERE"/*.provisioned.P2-AR-0039.py; do
  name="$(basename "$f" .py)"; name="${name%.derived.P2-AR-0039}"
  t="$(mktemp -d "$SCR/derived-$LABEL-$name-XXXXXX")"
  export P2AR0022_SHIM_LOG="$OUTD/$name.out.shimlog"; : > "$P2AR0022_SHIM_LOG"
  ( cd "$(dirname "$f")" && ALPHA_R_LIB="$LIB" GOV="$MIRROR/target/release/gov" GOV_BIN="$MIRROR/target/release/gov" PROBE_TMP="$t" SYNTH_SCRATCH="$t" timeout 900 python3 "$f" ) > "$OUTD/$name.out" 2>&1
  echo "[$name exit=$?]" >> "$OUTD/$name.out"
done
for f in "$OUTD"/*.out; do echo "$(basename "$f"): $(tail -n 1 "$f")"; done
