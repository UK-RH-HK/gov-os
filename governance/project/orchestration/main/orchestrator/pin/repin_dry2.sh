#!/usr/bin/env bash
# The second re-pin's dry run (DEC-933 item 1, P-REPIN-2): build the wheel of 5c401220 (w2/integrate after W2-57 and
# W2-07 round 2) twice from clean exports, in /tmp only, and print its sha256 and whether the two builds agree; check
# what the current pin's environment imports. It installs nothing and touches neither ~/.local/bin nor
# ~/.local/share/gov-os.
set -euo pipefail
C=5c401220
EPOCH=$(git -C /home/usain/Dynamic-Agentic-Engineering-OS log -1 --format=%ct 5c401220)
echo "commit $(git -C /home/usain/Dynamic-Agentic-Engineering-OS rev-parse 5c401220) epoch $EPOCH"
for n in 1 2; do
  rm -rf "/tmp/gov-repin2-dry-src-$n" "/tmp/gov-repin2-dry-wheel-$n"
  mkdir -p "/tmp/gov-repin2-dry-src-$n" "/tmp/gov-repin2-dry-wheel-$n"
  git -C /home/usain/Dynamic-Agentic-Engineering-OS archive "$C" | tar -x -C "/tmp/gov-repin2-dry-src-$n"
  SOURCE_DATE_EPOCH="$EPOCH" python3 -m pip wheel -q --no-deps --no-build-isolation --no-index -w "/tmp/gov-repin2-dry-wheel-$n" "/tmp/gov-repin2-dry-src-$n" > /dev/null
  sha256sum /tmp/gov-repin2-dry-wheel-$n/*.whl
done
/home/usain/.local/share/gov-os/pin-6a4696eb/bin/python -E -c 'import yaml, pytest, xdist, pytest_timeout, sqlite_vec; print("deps ok in pin-6a4696eb")'
# The new wheel holds W2-57's and W2-07's modules.
python3 -m zipfile -l /tmp/gov-repin2-dry-wheel-1/*.whl | grep -E "gov/close/(serial|gates)\.py" | awk '{print $1}'
