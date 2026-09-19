#!/usr/bin/env bash
# P2-AR-0020 (WS-8) — re-run the audit-of-record probes named by repair-delta for BC-P2-35..38, UNEDITED, from the
# merged evidence directories, against this worktree's target/release/gov.
#   alpha-r:   A2-01 (U2-U4), A2-02 (provisioned-ingress control), A2-03 (T1/T2), A2-04 (L1-L4), A2-05 (K6a/K6b/K6c),
#              A2-08 (V1-V3), S5-update (U-lines), S6-cross-machine (X3)
#   synthesis: AC16-X3 (X3a/X3b/X3c/X3d)
# Bytecode writing is disabled so nothing is written into another run's evidence directory.
# Usage: probes-rerun.sh <label>   (writes probes-<label>/<probe>.out beside this script)
set -u
LABEL="${1:?label}"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WT="$(cd "$HERE/../../../../.." && pwd)"
SCR="${P2AR0020_SCRATCH:?set P2AR0020_SCRATCH}"
OUTD="$HERE/probes-$LABEL"
mkdir -p "$OUTD"
export PYTHONDONTWRITEBYTECODE=1
for v in $(env | sed -n 's/^\(GOV_[A-Z_]*\)=.*/\1/p'); do unset "$v"; done
AR="$WT/release/capability-baseline/audit-0/alpha-r/evidence"
SY="$WT/release/capability-baseline/audit-0/synthesis/evidence"
{
  echo "# P2-AR-0020 probe re-run label=$LABEL"
  echo "# HEAD $(git -C "$WT" rev-parse HEAD) dirty-files: $(git -C "$WT" status --porcelain | wc -l) date $(date -u +%FT%TZ)"
  echo "# gov sha256 $(sha256sum "$WT/target/release/gov" | cut -d' ' -f1)"
  echo "# probe sources (sha256, must equal the audit-of-record files):"
  for f in A2-01-unprovisioned-posture.py A2-02-provisioned-ingress.py A2-03-post-install-tamper.py A2-04-lock-identity-and-masquerade.py \
           A2-05-rotation-revocation-recovery.py A2-08-reinstall-version-change.py S5-update.py S6-cross-machine.py lib/srr_mint.py lib/env.sh; do
    echo "  $(sha256sum "$AR/$f" | cut -d' ' -f1)  alpha-r/evidence/$f  (git: $(git -C "$WT" log -1 --format=%h -- "$AR/$f"))"
  done
  echo "  $(sha256sum "$SY/AC16-X3-ingress-root-of-trust-chain.py" | cut -d' ' -f1)  synthesis/evidence/AC16-X3-ingress-root-of-trust-chain.py"
  echo "  git diff vs HEAD of the probe dirs (must be empty): $(git -C "$WT" diff --stat HEAD -- "$AR" "$SY" | wc -l) lines"
} > "$OUTD/00-header.out"
run() {  # run <outname> <script>
  local name="$1" script="$2"
  local t; t="$(mktemp -d "$SCR/probe-$name-XXXXXX")"
  ( cd "$(dirname "$script")" && PROBE_TMP="$t" timeout 900 python3 "$(basename "$script")" ) > "$OUTD/$name.out" 2>&1
  echo "[$name exit=$?]" >> "$OUTD/$name.out"
}
run A2-01 "$AR/A2-01-unprovisioned-posture.py"
run A2-02 "$AR/A2-02-provisioned-ingress.py"
run A2-03 "$AR/A2-03-post-install-tamper.py"
run A2-04 "$AR/A2-04-lock-identity-and-masquerade.py"
run A2-05 "$AR/A2-05-rotation-revocation-recovery.py"
run A2-08 "$AR/A2-08-reinstall-version-change.py"
run S5-update "$AR/S5-update.py"
run S6-cross-machine "$AR/S6-cross-machine.py"
run AC16-X3 "$SY/AC16-X3-ingress-root-of-trust-chain.py"
ls -la "$OUTD"
