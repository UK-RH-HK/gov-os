#!/usr/bin/env bash
# P2-AR-0016 (WS-3): re-run the audit-of-record probes that repair-delta.md names for BC-P2-08/09/10/12/18/45/49,
# UNEDITED, from the merged evidence directories, against `target/release/gov` of this worktree (the probes resolve
# the binary from their own location). Each probe's own invocation convention is used; outputs go to $OUT.
#
#   OUT        output directory (created)
#   SCR        scratch directory for the disposable projects (created)
#   GOVX       optional: a gov binary to use instead (e.g. a role-declaring shim), passed through every convention
set -u
: "${OUT:?}" "${SCR:?}"
EVID="$(cd "$(dirname "$0")" && pwd)"
WT="$(cd "$EVID/../../../../.." && pwd)"
A="$WT/release/capability-baseline/audit-0"
mkdir -p "$OUT" "$SCR"
export PATH="$HOME/.cargo/bin:$PATH"
unset GOV_ROLE GOV_SESSION GOV_MACHINE_STATE_DIR
BIN="${GOVX:-$WT/target/release/gov}"
echo "binary: $BIN ($(sha256sum "$BIN" | cut -c1-16))" | tee -a "$OUT/00-binary.txt"
t() { # t <name> <cmd...>   (ONLY=<substring> restricts the run to matching probe names)
  local name="$1"; shift
  if [ -n "${ONLY:-}" ] && [[ "$name" != *"$ONLY"* ]]; then return 0; fi
  echo "### $name" >&2
  ( "$@" ) > "$OUT/$name.out" 2>&1
  echo "exit=$?" >> "$OUT/$name.out"
}
cd "$A/delta-r/evidence"
for p in L3-gate-presentation-attacks L3-supplement L2-decision-package L1-contradiction-resolution M1-M3-routing; do
  t "delta-r.$p" env GOV_BIN="$BIN" PROBE_SCRATCH="$SCR/delta-$p" python3 "$p.py"
done
cd "$A/gamma-r/evidence"
for p in E1-authority H2H3-readiness F4-plugins FRESH-invalidation; do
  t "gamma-r.$p" env GOV="$BIN" WT="$WT" PROBES="$SCR/gamma-$p" bash "$p.sh"
done
cd "$A/alpha-r/evidence"
for p in S3-S4-role-flag-authority A5-emergency-controls; do
  mkdir -p "$SCR/alpha-$p"
  t "alpha-r.$p" env GOV="$BIN" PROBE_TMP="$SCR/alpha-$p" python3 "$p.py"
done
cd "$WT"
t "epsilon-r.O5-G0-guard-matrix" env GOV="$BIN" WT="$WT" SCRATCH="$SCR/eps-g0" python3 "$A/epsilon-r/evidence/O5-G0-guard-matrix.py"
t "epsilon-r.O5-G0-focus" env GOV="$BIN" WT="$WT" SCRATCH="$SCR/eps-focus" bash "$A/epsilon-r/evidence/O5-G0-focus.sh"
t "epsilon-r.Q-learning-upstream" env GOV="$BIN" WT="$WT" SCRATCH="$SCR/eps-q" bash "$A/epsilon-r/evidence/Q-learning-upstream.sh"
cd "$A/zeta-r/evidence"
mkdir -p "$SCR/zeta"
t "zeta-r.W03-task-input-manifest" env GOV="$BIN" ZPROBE_SCRATCH="$SCR/zeta" python3 W03-task-input-manifest.py
cd "$WT"
t "synthesis.AC16-X2-authority-gate-chain" env GOV_BIN="$BIN" SYNTH_SCRATCH="$SCR/x2" python3 "$A/synthesis/evidence/AC16-X2-authority-gate-chain.py"
echo done >&2
