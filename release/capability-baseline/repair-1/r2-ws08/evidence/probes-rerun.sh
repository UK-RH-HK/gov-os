#!/usr/bin/env bash
# P2-AR-0029 (WS-8, round 2) — re-run the audit-of-record probes the repair delta names for BC-P2-35 / BC-P2-36
# (and the WS-8 neighbours they share code with), UNEDITED, against one tree's target/release/gov.
#   alpha-r:   A2-01 (U2-U4 unprovisioned posture), A2-02 (provisioned-ingress control), A2-03 (T1/T2 post-install
#              tamper), A2-04 (L1-L4 lock identity), A2-05 (rotation/recovery), A2-08 (reinstall), S5-update,
#              S6-cross-machine
#   synthesis: AC16-X3 (X3a unprovisioned / X3b provisioned control / X3c consistent rewrite / X3d)
# The probe files are run from <tree>/release/capability-baseline/audit-0/..., so each probe uses that tree's own
# target/release/gov and framework (a `git archive` export of the base commit for "before", this worktree for
# "after"); their sha256 is printed and must be identical for both trees. Output goes only to this evidence
# directory; bytecode writing is disabled so nothing is written beside the probes.
#
# The audit-of-record probes predate WS-3 (BC-P2-08/-10/-49): unedited, they declare no role and stop at
# AUTHORITY_DENIED before any root-of-trust line runs. They are therefore reached exactly as the integration builder
# reached them (repair-1/integration/evidence/audit-probes/run-audit-probe.sh, mode `shim`): through a scratch MIRROR
# of the tree (symlinks to every entry) whose target/release/gov runs the integration builder's evidence adapter
# gov-owner-channel-shim.py, which only (a) declares `--role orchestrator` where a probe declared no role, (b) turns a
# relayed human `decide` on an already-rendered gate into an owner-signed answer and (c) fills absent gate-package
# fields; every other invocation, including every lifecycle ingress, reaches the real binary byte-for-byte. The
# adapter's log is kept beside each output (<probe>.out.shimlog).
# Usage: probes-rerun.sh <label> <tree>   (writes probes-<label>/<probe>.out beside this script)
set -u
LABEL="${1:?label}"; TREE="$(cd "${2:?tree}" && pwd)"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WT="$(cd "$HERE/../../../../.." && pwd)"
SCR="${P2AR0029_SCRATCH:-$(cd "$WT/../.." && pwd)/p2-ar-0029-probes}"
OUTD="$HERE/probes-$LABEL"
mkdir -p "$OUTD" "$SCR"
export PYTHONDONTWRITEBYTECODE=1
for v in $(env | sed -n 's/^\(GOV_[A-Z_]*\)=.*/\1/p'); do unset "$v"; done
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
AR="$MIRROR/release/capability-baseline/audit-0/alpha-r/evidence"
SY="$MIRROR/release/capability-baseline/audit-0/synthesis/evidence"
{
  echo "# P2-AR-0029 probe re-run label=$LABEL"
  echo "# tree $TREE (HEAD $(git -C "$TREE" rev-parse HEAD 2>/dev/null) dirty-files: $(git -C "$TREE" status --porcelain 2>/dev/null | wc -l))"
  echo "# date $(date -u +%FT%TZ)"
  echo "# gov $TREE/target/release/gov sha256 $(sha256sum "$TREE/target/release/gov" | cut -d' ' -f1) (reached via $MIRROR/target/release/gov = the integration evidence adapter)"
  echo "# adapter sha256 $(sha256sum "$WT/release/capability-baseline/repair-1/integration/evidence/audit-probes/gov-owner-channel-shim.py" | cut -d' ' -f1)"
  echo "# probe sources (sha256; identical in both trees = the audit-of-record files):"
  for f in A2-01-unprovisioned-posture.py A2-02-provisioned-ingress.py A2-03-post-install-tamper.py A2-04-lock-identity-and-masquerade.py \
           A2-05-rotation-revocation-recovery.py A2-08-reinstall-version-change.py S5-update.py S6-cross-machine.py lib/srr_mint.py lib/env.sh; do
    echo "  $(sha256sum "$AR/$f" | cut -d' ' -f1)  alpha-r/evidence/$f  (worktree copy: $(sha256sum "$WT/release/capability-baseline/audit-0/alpha-r/evidence/$f" | cut -d' ' -f1))"
  done
  echo "  $(sha256sum "$SY/AC16-X3-ingress-root-of-trust-chain.py" | cut -d' ' -f1)  synthesis/evidence/AC16-X3-ingress-root-of-trust-chain.py  (worktree copy: $(sha256sum "$WT/release/capability-baseline/audit-0/synthesis/evidence/AC16-X3-ingress-root-of-trust-chain.py" | cut -d' ' -f1))"
} > "$OUTD/00-header.out"
run() {  # run <outname> <script>
  local name="$1" script="$2"
  local t; t="$(mktemp -d "$SCR/probe-$LABEL-$name-XXXXXX")"
  export P2AR0022_SHIM_LOG="$OUTD/$name.out.shimlog"; : > "$P2AR0022_SHIM_LOG"
  ( cd "$(dirname "$script")" && GOV="$MIRROR/target/release/gov" GOV_BIN="$MIRROR/target/release/gov" PROBE_TMP="$t" SYNTH_SCRATCH="$t" timeout 900 python3 "$(basename "$script")" ) > "$OUTD/$name.out" 2>&1
  echo "[$name exit=$?]" >> "$OUTD/$name.out"
}
for p in "$@"; do :; done
PROBES="${PROBES:-A2-01 A2-02 A2-03 A2-04 A2-05 A2-08 S5-update S6-cross-machine AC16-X3}"
for p in $PROBES; do
  case "$p" in
    A2-01) run A2-01 "$AR/A2-01-unprovisioned-posture.py" ;;
    A2-02) run A2-02 "$AR/A2-02-provisioned-ingress.py" ;;
    A2-03) run A2-03 "$AR/A2-03-post-install-tamper.py" ;;
    A2-04) run A2-04 "$AR/A2-04-lock-identity-and-masquerade.py" ;;
    A2-05) run A2-05 "$AR/A2-05-rotation-revocation-recovery.py" ;;
    A2-08) run A2-08 "$AR/A2-08-reinstall-version-change.py" ;;
    S5-update) run S5-update "$AR/S5-update.py" ;;
    S6-cross-machine) run S6-cross-machine "$AR/S6-cross-machine.py" ;;
    AC16-X3) run AC16-X3 "$SY/AC16-X3-ingress-root-of-trust-chain.py" ;;
  esac
done
ls "$OUTD"
