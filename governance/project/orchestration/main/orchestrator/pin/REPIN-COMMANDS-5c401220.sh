#!/usr/bin/env bash
# The second re-pin (DEC-933 item 1, P-REPIN-2 (a)): the owner's act. W2-57 and W2-07 round 2 in the judge.
# Run in a plain terminal (not inside a Claude session: it reinstalls gov, DEC-928 item 3), with no Claude session
# running a gov command (the orchestrator confirms the leads are idle and no close or nightly runs before the ACT).
# No settings regeneration: nothing under template/ changed since 6a4696eb.
set -euo pipefail
R=/home/usain/Dynamic-Agentic-Engineering-OS
P="$HOME/.local/share/gov-os"
C=5c401220
W="$P/wheels/$C/gov-0.1.0-py3-none-any.whl"

# A1. A clean export of 5c401220
git -C "$R" cat-file -e "$C^{commit}"
rm -rf /tmp/gov-pin-src-$C && mkdir /tmp/gov-pin-src-$C
git -C "$R" archive "$C" | tar -x -C /tmp/gov-pin-src-$C

# A2. The wheel, reproducible (the commit's own time); offline. The orchestrator's dry run built it twice from clean
#     exports with this sha256.
mkdir -p "$P/wheels/$C"
SOURCE_DATE_EPOCH=1793182278 python3 -m pip wheel --no-deps --no-build-isolation --no-index -w "$P/wheels/$C" /tmp/gov-pin-src-$C
echo "e4f35131d8cff32f124863c6780efad368c2500be59824dc7fe9458d126905d0  $W" | sha256sum -c -

# A3. Its own environment, non-editable. pin-6a4696eb is left in place for the rollback.
python3 -m venv --system-site-packages "$P/pin-$C"
"$P/pin-$C/bin/python" -m pip install --no-deps --no-index "$W"

# A4. Point gov at the new pin
ln -sfn "$P/pin-$C/bin/gov" "$HOME/.local/bin/gov"
hash -r

# A5. Verify
readlink -f "$(command -v gov)"                                                  # .../pin-5c401220/bin/gov
"$P/pin-$C/bin/python" -E -c 'import gov; print(gov.__file__)'                   # .../pin-5c401220/lib/python3.12/site-packages/gov/__init__.py
"$P/pin-$C/bin/python" -E -c 'import gov.close.serial, gov.close.gates; print("W2-57 and W2-07 in the pin")'
"$P/pin-$C/bin/python" -E -c 'import yaml, pytest, xdist, pytest_timeout, sqlite_vec; print("deps ok")'
gov --help | head -1                                                             # usage: gov [-h] <command> ...

# A6. The registry entry (refuses unless A2-A4 hold); then commit it
python3 "$R/.gov-runtime/scratch/orchestrator/pin/repin2_registry.py"
git -C "$R" commit -m "DEC-933: the second re-pin, gov from the wheel of 5c401220 (W2-57, W2-07 round 2)" \
  --trailer "Task: decision-record" --trailer "Implements: DEC-933" --trailer "Role: owner" -- governance/project/tool-registry.yaml

# ---- Rollback (one command; the first re-pin's judge comes back) --------------------------------------------------
#   ln -sfn "$P/pin-6a4696eb/bin/gov" "$HOME/.local/bin/gov"; hash -r
#   then revert the registry commit.
