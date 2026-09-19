#!/usr/bin/env bash
# P2-AR-0032 — P2-HO-0030 "Secret-like literal": WS-2's framework/health/SKILL_SCENARIO_CHECKS.yaml carries a planted
# `AKIA…EXAMPLE` literal (SKL-MEMORY-RECONSTRUCTION V1) that the kernel's own secret scanner flags if installed. Its
# semantics are not changed here (WS-2 round 3); this shows that no integrated test installs it into a scanned project.
# Usage: check-secret-literal.sh <minutes>   (inspects the certification scratch trees written in the last <minutes>)
set -u
MIN="${1:-120}"
WT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../../../.." && pwd)"
echo "# worktree $WT HEAD $(git -C "$WT" rev-parse HEAD)"
echo "# 1. the kernel payload the product installs (framework/KERNEL.yaml payload_dirs; kernel::stage_payload copies only these):"
sed -n '/^payload_dirs:/,/^[a-z_]*:/p' "$WT/framework/KERNEL.yaml" | grep '^  - ' | tr -d ' -' | tr '\n' ' '; echo
echo "#    'health' in payload_dirs: $(sed -n '/^payload_dirs:/,/^[a-z_]*:/p' "$WT/framework/KERNEL.yaml" | grep -c '^  - health$')"
echo "# 2. where the literal is in the canonical tree:"
grep -rn --include=*.yaml "AKIAIOSFODNN7EXAMPLE" "$WT/framework" | sed "s|$WT/||" | cut -c1-140
echo "# 3. certification scratch trees (/tmp/gov-cert-*, last $MIN min):"
DIRS=$(find /tmp -maxdepth 1 -name 'gov-cert-*' -mmin -"$MIN" -type d)
echo "#    trees: $(echo "$DIRS" | grep -c .)"
echo "#    governed projects (framework.lock) whose installed kernel carries health/: $(for d in $DIRS; do [ -f "$d/governance/framework.lock" ] && [ -e "$d/governance/kernel/health" ] && echo "$d"; done | grep -c .)"
echo "#    installed kernels anywhere under the trees carrying health/: $(for d in $DIRS; do find "$d" -path '*/governance/kernel/health' -not -path '*/.git/*' 2>/dev/null; done | grep -c .)"
echo "#    files holding framework/health/SKILL_SCENARIO_CHECKS.yaml, by kind of tree:"
for d in $DIRS; do
  for f in $(find "$d" -path '*/health/SKILL_SCENARIO_CHECKS.yaml' -not -path '*/.git/*' 2>/dev/null); do
    top="$(basename "$d" | sed 's/-[0-9a-f]\{16,\}$//')"
    rel="${f#$d/}"
    gp="$( [ -f "$d/governance/framework.lock" ] && echo governed-project || echo not-a-governed-project)"
    echo "$top  ${rel%%/health/*}/health/…  $gp"
  done
done | sort | uniq -c
