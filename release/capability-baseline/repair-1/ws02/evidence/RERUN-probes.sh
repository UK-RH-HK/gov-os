#!/usr/bin/env bash
# P2-AR-0015 (WS-2) — re-run the audit-of-record probes named by repair-delta §1 for BC-P2-03/-06/-42/-43, UNEDITED,
# from the merged evidence directories, against a worktree's target/release/gov.
#
#   bash RERUN-probes.sh <worktree-root> <out-dir> [probe ...]
#
# <worktree-root> is the tree whose release binary and framework are exercised: this worktree for the "after" runs,
# a `git archive` of the base commit (c6b60bc) with the base binary at target/release/gov for the "before" runs.
# Every run gets a private scratch directory and a private embedded-kernel cache (GOV_KERNEL_CACHE): the per-user
# default ~/.cache/gov/kernels is shared by concurrent builders on this machine and was observed partially emptied
# by another process during this session, which makes `gov init` from the embedded payload fail with UNKNOWN_ROLE.
# Probe names: O5 O4 O1 O2 U alpha beta delta zeta gamma X1 (default: all).
set -u
WT="$(cd "$1" && pwd)"; OUT="$(mkdir -p "$2" && cd "$2" && pwd)"; shift 2
PROBES=("$@"); [ ${#PROBES[@]} -eq 0 ] && PROBES=(O5 O4 O1 O2 U alpha beta delta zeta gamma X1)
BASE="${WS02_SCRATCH_BASE:-$(mktemp -d)}"; mkdir -p "$BASE/kcache"
export GOV_KERNEL_CACHE="$BASE/kcache"
A="$WT/release/capability-baseline/audit-0"
scratch() { mktemp -d -p "$BASE"; }
for p in "${PROBES[@]}"; do
  case "$p" in
    O5)    (cd "$WT" && SCRATCH=$(scratch) timeout 1200 bash "$A/epsilon-r/evidence/O5-scheduler-requirements.sh") > "$OUT/O5-scheduler-requirements.out" 2>&1 ;;
    O4)    (cd "$WT" && SCRATCH=$(scratch) timeout 1200 bash "$A/epsilon-r/evidence/O4-suite-currency.sh") > "$OUT/O4-suite-currency.out" 2>&1 ;;
    O1)    (cd "$WT" && SCRATCH=$(scratch) timeout 1200 bash "$A/epsilon-r/evidence/O1-product-families.sh") > "$OUT/O1-product-families.out" 2>&1 ;;
    O2)    (cd "$WT" && SCRATCH=$(scratch) timeout 1500 bash "$A/epsilon-r/evidence/O2-governance-families.sh") > "$OUT/O2-governance-families.out" 2>&1 ;;
    U)     (cd "$WT" && SCRATCH=$(scratch) timeout 1500 bash "$A/epsilon-r/evidence/U-slos-and-healthy.sh") > "$OUT/U-slos-and-healthy.out" 2>&1 ;;
    alpha) (cd "$A/alpha-r/evidence" && PROBE_TMP=$(scratch) timeout 1200 python3 FRESH-invalidation.py) > "$OUT/alpha-r-FRESH-invalidation.out" 2>&1 ;;
    beta)  (cd "$A/beta-r/evidence" && PROBE_TMP=$(scratch) timeout 1200 python3 FRESH-evidence-invalidation.py) > "$OUT/beta-r-FRESH-evidence-invalidation.out" 2>&1 ;;
    delta) (cd "$A/delta-r/evidence" && PROBE_SCRATCH=$(scratch) timeout 1200 python3 FRESH-invalidation.py) > "$OUT/delta-r-FRESH-invalidation.out" 2>&1 ;;
    zeta)  (cd "$A/zeta-r/evidence" && ZPROBE_SCRATCH=$(scratch) timeout 1200 python3 FR-freshness-invalidation.py) > "$OUT/zeta-r-FR-freshness-invalidation.out" 2>&1 ;;
    gamma) (cd "$WT" && PROBES=$(scratch) timeout 1200 bash "$A/gamma-r/evidence/F1-skills.sh") > "$OUT/gamma-r-F1-skills.out" 2>&1 ;;
    X1)    (cd "$WT" && SYNTH_SCRATCH=$(scratch) timeout 1200 python3 "$A/synthesis/evidence/AC16-X1-upstream-change-chain.py") > "$OUT/AC16-X1-upstream-change-chain.out" 2>&1 ;;
    *) echo "unknown probe $p" >&2 ;;
  esac
  echo "$p done: $(date -u +%FT%TZ)"
done
echo "binary: $(sha256sum "$WT/target/release/gov" | cut -c1-64)" > "$OUT/BINARY.txt"
