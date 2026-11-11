#!/usr/bin/env bash
# Lead's own repeat of S6: the new file on the ACT's parent's two data files (S1-S4 must be red), then on the branch's own (green).
set -u
T=/tmp/gov-os-lead-W2-66c
C=$T/clone
LOG=/home/usain/gov-os-worktrees/W2-66c/.gov-runtime/scratch/lead/log
F=tests/acceptance/W2-66/test_w2_66_select_fixes.py
rm -rf "$C"
git clone --quiet --branch w2/W2-66c-tests /home/usain/gov-os-worktrees/W2-66c-tests "$C" || exit 9
git -C "$C" rev-parse --short=12 HEAD > "$LOG/s6-clone-head.txt"
run() {
  ( cd "$C" && env HOME=$T/empty-home PYTHONUSERBASE=/home/usain/.local TMPDIR=$T PYTHONPATH=$C/src \
      python3 -m pytest "$F" -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -rA \
      --junitxml="$LOG/s6-$1.xml" ) > "$LOG/s6-$1.txt" 2>&1
  echo "$1 exit $?" >> "$LOG/s6-summary.txt"
}
: > "$LOG/s6-summary.txt"
git -C "$C" show 795d97c7cd44:governance/project/test-map.yaml > "$C/governance/project/test-map.yaml"
git -C "$C" show 795d97c7cd44:tests/optin-lifted-breadth.txt > "$C/tests/optin-lifted-breadth.txt"
run parent
git -C "$C" show 8038e0ee648c:governance/project/test-map.yaml > "$C/governance/project/test-map.yaml"
git -C "$C" show 8038e0ee648c:tests/optin-lifted-breadth.txt > "$C/tests/optin-lifted-breadth.txt"
run act
git -C "$C" checkout --quiet -- governance/project/test-map.yaml tests/optin-lifted-breadth.txt
git -C "$C" status --short >> "$LOG/s6-summary.txt"
run head
rm -rf "$C"
echo done >> "$LOG/s6-summary.txt"
