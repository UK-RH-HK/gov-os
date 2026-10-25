#!/usr/bin/env bash
# The first re-pin's dry run (DEC-884, DEC-921): build the wheel of the merge commit twice from clean exports, in /tmp
# only, and print its sha256 and whether the two builds agree; check what the current pin's environment imports. It
# installs nothing and touches neither ~/.local/bin nor ~/.local/share/gov-os.
set -euo pipefail
R=/home/usain/Dynamic-Agentic-Engineering-OS
C=6a4696eb
EPOCH=$(git -C /home/usain/Dynamic-Agentic-Engineering-OS log -1 --format=%ct 6a4696eb)
echo "commit $(git -C /home/usain/Dynamic-Agentic-Engineering-OS rev-parse 6a4696eb) epoch $EPOCH"
for n in 1 2; do
  rm -rf "/tmp/gov-repin-dry-src-$n" "/tmp/gov-repin-dry-wheel-$n"
  mkdir -p "/tmp/gov-repin-dry-src-$n" "/tmp/gov-repin-dry-wheel-$n"
  git -C /home/usain/Dynamic-Agentic-Engineering-OS archive 6a4696eb | tar -x -C "/tmp/gov-repin-dry-src-$n"
  SOURCE_DATE_EPOCH="$EPOCH" python3 -m pip wheel -q --no-deps --no-build-isolation --no-index -w "/tmp/gov-repin-dry-wheel-$n" "/tmp/gov-repin-dry-src-$n" > /dev/null
  sha256sum /tmp/gov-repin-dry-wheel-$n/*.whl
done
/home/usain/.local/share/gov-os/pin-fecb870c/bin/python -c 'import yaml, pytest, xdist, sqlite_vec; print("deps ok")'
/home/usain/.local/share/gov-os/pin-fecb870c/bin/python -c 'import pytest_timeout; print("pytest_timeout", pytest_timeout.__file__)' 2>&1 | tail -1
python3 -c 'import pytest_timeout; print("system pytest_timeout", pytest_timeout.__file__)' 2>&1 | tail -1
