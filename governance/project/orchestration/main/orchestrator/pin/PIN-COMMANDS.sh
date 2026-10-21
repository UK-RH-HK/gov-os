#!/usr/bin/env bash
# DEC-822 step 1, the bootstrap pin: the owner's act. Run in a plain terminal (not inside a Claude session),
# AFTER committing the staged batch, with no Claude session running a gov command.
set -euo pipefail
R=/home/usain/Dynamic-Agentic-Engineering-OS
P="$HOME/.local/share/gov-os"
W="$P/wheels/fecb870c/gov-0.1.0-py3-none-any.whl"

# 1. A clean export of fecb870c (no working-tree edits, no ignored files)
rm -rf /tmp/gov-pin-src && mkdir /tmp/gov-pin-src
git -C "$R" archive fecb870c | tar -x -C /tmp/gov-pin-src

# 2. The wheel, reproducible (the commit's own time); offline, no build download
mkdir -p "$P/wheels/fecb870c"
SOURCE_DATE_EPOCH=1792407780 python3 -m pip wheel --no-deps --no-build-isolation --no-index -w "$P/wheels/fecb870c" /tmp/gov-pin-src
echo "385fd5f0eceb04e926be2294149cc761235855fb5e13dd31ba9e1cefe3d5f7bd  $W" | sha256sum -c -

# 3. Its own environment, non-editable (system + user site packages give PyYAML, pytest, xdist, sqlite-vec)
python3 -m venv --system-site-packages "$P/pin-fecb870c"
"$P/pin-fecb870c/bin/python" -m pip install --no-deps --no-index "$W"

# 4. In place of the editable install (removes ~/.local/bin/gov and the editable hook)
python3 -m pip uninstall -y --break-system-packages gov
ln -sfn "$P/pin-fecb870c/bin/gov" "$HOME/.local/bin/gov"
hash -r

# 5. Verify
readlink -f "$(command -v gov)"                                     # .../pin-fecb870c/bin/gov
"$P/pin-fecb870c/bin/python" -c 'import gov; print(gov.__file__)'   # .../pin-fecb870c/lib/python3.12/site-packages/gov/__init__.py
"$P/pin-fecb870c/bin/python" -c 'import yaml, pytest, xdist, sqlite_vec; print("deps ok")'
python3 -c 'import gov' 2>&1 | tail -1                              # ModuleNotFoundError: expected
gov --help | head -1                                                # usage: gov [-h] <command> ...

# 6. The registry entry (refuses unless steps 2-4 hold); then commit it
python3 "$R/.gov-runtime/scratch/orchestrator/pin/pin_registry.py"
# git -C "$R" commit -m "DEC-822 step 1: the bootstrap pin, gov from the wheel of fecb870c" \
#   --trailer "Task: decision-record" --trailer "Implements: DEC-822" --trailer "Role: owner" -- governance/project/tool-registry.yaml

# Rollback (back to DEC-605's editable install):
#   rm "$HOME/.local/bin/gov"; python3 -m pip install --user --break-system-packages --no-build-isolation --no-index -e "$R"
#   git -C "$R" checkout -- governance/project/tool-registry.yaml
